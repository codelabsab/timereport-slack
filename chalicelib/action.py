import logging
import json
from chalicelib.lib.list import get_list_data
from chalicelib.lib.api import read_lock, read_event
from chalicelib.lib.helpers import parse_date, date_range
from chalicelib.lib.slack import (
    submit_message_menu,
    slack_client_responder,
    delete_message_menu,
    Slack,
)
from typing import Dict
from chalicelib.model.event import create_lock
from datetime import datetime
from chalicelib.lib.lock import lock_event

log = logging.getLogger(__name__)


class Action:
    def __init__(self, payload, config):
        self.payload = payload

        try:
            self.params = self.payload["text"][0].split()
        except KeyError:
            log.info("No parameters received. Defaulting to help action")
            self.params = ["help"]

        self.config = config
        self.bot_access_token = config["bot_access_token"]
        self.slack = Slack(slack_token=config["bot_access_token"])
        self.response_url = self.payload["response_url"][0]
        self.format_str = self.config.get("format_str")
        self.actions = dict(
            add=self._add_action,
            edit=self._edit_action,
            delete=self._delete_action,
            list=self._list_action,
            lock=self._lock_action,
            help=self._help_action,
        )

    def perform_action(self):
        """
        Perform action.

        Supported actions are:
        add - Add one or more events in timereport
        edit - Edit a single event in timereport
        delete - Delete event in timereport
        list - List one or more events in timereport
        lock - Not implemented yet
        help - Provide this helpful output
        help <action> - Provide helpful output for specific action
        """

        self.action = self.params[0]
        self.arguments = self.params[1:]
        self.user_id = self.payload["user_id"][0]
        self.user_name = self.payload["user_name"][0]

        log.debug(f"Action is: {self.action}")
        log.debug(f"Arguments are: {self.arguments}")

        action_fn = self.actions.get(self.action, self._unsupported_action)
        return action_fn()

    def _unsupported_action(self):
        log.info(f"Action: {self.action} is not supported")
        return self.send_response(message=f"Unsupported action: {self.action}")

    def _add_action(self):
        """
        Add one or more events in timereport

        /timereport add <reason> <day> <hours>

        <reason> can be:
         * vab
         * sjuk
         * intern
         * semester


        <day> can be
        "today" - Add event for todays date
        a date of the format "2020-03-10" or a range such as "2020-03-10:2020-03-17"
        """

        # validate number of arguments
        if not self._valid_number_of_args(min_args=2, max_args=3):
            log.debug(f"args: {self.arguments}")
            return self.send_response(message="Wrong number of args for add command")

        # assign
        reason: str = self.arguments[0]
        input_date: str = self.arguments[1]
        hours: str = self.arguments[2] if len(self.arguments) == 3 else 8

        # validate reason
        if not self._valid_reason(reason=reason):
            return self.send_response(message=f"Reason {reason} is not valid")

        # validate hours
        try:
            hours: int = round(float(hours))
        except ValueError:
            return self.send_response(message=f"Could not parse hours: {hours}")

        # validate dates
        parsed_dates: Dict[str, datetime] = parse_date(
            date=input_date, format_str=self.format_str
        )
        if parsed_dates["to"] is None or parsed_dates["from"] is None:
            self.send_response(message="failed to parse date {date}")

        # validate months in date argument are not locked
        if self._check_locks(date=parsed_dates["from"], second_date=parsed_dates["to"]):
            return self.send_response(
                message=f"Unable to add since one or more month in range are locked :cry:"
            )

        # all validation completed successfully - send interactive menu with range from parsed_dates
        self.send_attachment(
            attachment=submit_message_menu(
                user_name=self.user_name,
                reason=reason,
                date=f"{input_date}",
                hours=hours,
            )
        )
        return ""

    def _list_action(self):
        """
        List timereport for user.
        If no arguments supplied it will default to all.

        Supported arguments:
        "today" - List the event for the todays date
        "date" - The date as a string.
        """
        arguments = self.params[1:]

        log.debug(f"Got arguments: {arguments}")
        try:
            if arguments[0] == "today":
                date_str = datetime.now().strftime("%Y-%m-%d")
            else:
                date_str = arguments[0]
        except IndexError:
            month = datetime.now().strftime("%Y-%m")
            # A hack to set the date_str to the current month
            date_str = f"{month}-01:{month}-31"
            arguments = self.params[1:]
        except Exception as error:
            log.debug(f"got unexpected exception: {error}", exc_info=True)
            self.send_response(
                message=f"Got unexpected error with arguments: {arguments}"
            )
            return ""

        log.debug(f"The date string set to: {date_str}")
        list_data = self._get_events(date_str=date_str)

        if not list_data or list_data == "[]":
            log.debug(f"List returned nothing. Date string was: {date_str}")
            self.send_response(
                message=f"Sorry, nothing to list with supplied argument {arguments}"
            )
            return ""

        self._create_list_message(data=list_data)
        self.slack.post_message(message="From timereport", channel=self.user_id)
        return ""

    def _delete_action(self):

        date_string = self.params[1]
        date: Dict[str, datetime] = parse_date(date_string, format_str=self.format_str)

        if date["from"] is None or date["to"] is None:
            return self.send_response(message=f"Could not parse date {date_string}")

        if date["from"] != date["to"]:
            return self.send_response(
                message=f"Delete doesn't support date range :cry:"
            )

        if not self._check_locks(date=date["from"], second_date=date["to"]):
            self.send_attachment(
                attachment=delete_message_menu(
                    self.payload.get("user_name")[0], date_string
                )
            )
        else:
            self.send_response(message=f"Unable to delete since month is locked :cry:")
        return ""

    def _edit_action(self):
        """
        Edit event in timereport for user.
        If no arguments supplied it will try to edit today.

        /timereport edit <reason> <date> <hours>

        Example: /timereport edit vab 2019-01-01 4
        """

        if not self._valid_number_of_args(min_args=2, max_args=3):
            self.send_response(message="Got the wrong number of arguments")

        reason = self.arguments[0]
        hours = 8

        if not self._valid_reason(reason=reason):
            return self.send_response(message=f"Reason {reason} is not valid")

        try:
            date_input = self.arguments[1]
        except IndexError:
            date_input = "today"
            log.debug(f"Didn't get any params. Setting date to {date_input}")

        try:
            hours = round(float(self.arguments[2]))
        except ValueError as error:
            log.error(f"Failed to parse hours. Error was: {error}")
            return self.send_response(message="Could not parse hours")
        except TypeError as error:
            log.debug(f"Caught error: {error}")
            log.info(f"Using default hours '{hours}'")

        date: Dict[str, datetime] = parse_date(date_input, format_str=self.format_str)
        if date["from"] is None or date["to"] is None:
            self.send_response(message="failed to parse date {date_string}")

        if date["from"] is not date["to"]:
            return self.send_response(message=f"Edit doesn't support date range :cry:")

        if self._check_locks(date=date["from"], second_date=date["to"]):
            return self.send_response(
                message=f"Can't edit date {date_input} because locked month :cry:"
            )

        event_to_edit = read_event(
            url=self.config["backend_url"], user_id=self.user_id, date=date_input
        )

        if event_to_edit.status_code != 200:
            log.error(f"Response code from API: {event_to_edit.status_code}")
            return self.send_response(
                message=f"Something went wrong fetching event to edit. :cry:"
            )

        log.debug(f"Event to edit is: {event_to_edit.json()}")
        if not event_to_edit.json():
            self.send_response(message=f"No event for date {date} to edit. :shrug:")
            return ""

        self.send_attachment(
            attachment=submit_message_menu(self.user_name, reason, date_input, hours)
        )

        return ""

    def send_response(self, message):
        """
        Send a response to slack

        :message: The Message to send
        """

        log.debug("Sending message to slack")
        self.slack.post_message(channel=self.user_id, message=message)

        return ""

    def send_attachment(self, attachment):
        """
        Send an message to slack using attachment
        :attachment: The attachment (slack specific attachment) to send
        """

        slack_client_response = slack_client_responder(
            token=self.bot_access_token, user_id=self.user_id, attachment=attachment
        )

        if slack_client_response.status_code != 200:
            log.error(
                f"""Failed to send response to slack. Status code was: {slack_client_response.status_code}.
                The response from slack was: {slack_client_response.text}"""
            )
            return "Slack response to user failed"
        else:
            log.debug(f"Slack client response was: {slack_client_response.text}")
        return slack_client_response

    def _help_action(self):
        """
        Nothing to see here.. Try another action :)
        """
        action_fn = self.perform_action
        if len(self.arguments) > 0:
            action_fn = self.actions.get(self.arguments[0], self.perform_action)
        return self.send_response(message=f"{action_fn.__doc__}")

    def _get_events(self, date_str):
        return get_list_data(
            f"{self.config['backend_url']}", self.user_id, date_str=date_str
        )

    def _lock_action(self):
        """
        Lock the timereport for month

        create lock:
        /timereport lock 2019-08

        list locks:
        /timereport list 2020
        """

        if not self._valid_number_of_args(min_args=1, max_args=2):
            return self.send_response(
                message=f"Got the wrong number of arguments for {self.action}. See these examples: {self._lock_action.__doc__}"
            )

        if self.arguments[0] == "list":
            year = None

            try:
                year = int(self.arguments[1])
            except IndexError:
                now = datetime.now()
                year = now.year

            locks = self._check_locks(
                date=datetime(year, 1, 1), second_date=datetime(year, 12, 1),
            )

            return self.send_response(f"Locks: {locks}")

        event = create_lock(user_id=self.user_id, event_date=self.arguments[0])
        log.debug(f"lock event: {event}")

        response = lock_event(url=self.config["backend_url"], event=json.dumps(event))
        log.debug(f"response was: {response.text}")
        if response.status_code == 200:
            self.send_response(message=f"Lock successful! :lock: :+1:")
            return ""
        else:
            self.send_response(message=f"Lock failed! :cry:")
            return ""

    def _check_locks(self, date: datetime, second_date: datetime) -> list:
        """
        Check dates for lock.
        """
        dates_to_check = list()
        locked_dates = list()
        for date in date_range(start_date=date, stop_date=second_date):
            if not date.strftime("%Y-%m") in dates_to_check:
                dates_to_check.append(date.strftime("%Y-%m"))

        log.debug(f"Got {len(dates_to_check)} date(s) to check")
        for date in dates_to_check:
            response = read_lock(
                url=self.config["backend_url"], user_id=self.user_id, date=date
            )
            if response.json():
                log.info(f"Date {date} is locked")
                dates_to_check.append(response.json())
                locked_dates.append(date)

        return locked_dates

    def _valid_number_of_args(self, min_args: int, max_args: int) -> bool:
        """
        Check that the number of arguments in the list is within the valid range
        """
        log.debug(f"Got {len(self.arguments)} number of args")
        if min_args <= len(self.arguments) <= max_args:
            return True
        return False

    def _valid_reason(self, reason: str) -> bool:
        """
        Check that reason is valid
        """

        if reason in self.config.get("valid_reasons"):
            return True

        return False

    def _create_list_message(self, data) -> None:
        """
        Create the slack block message layout for list action
        """
        data = json.loads(data)

        start_date = data[0].get("event_date")
        end_date = data[-1].get("event_date")

        self.slack.add_section_block(
            text=f"Reported time for period *{start_date}:{end_date}*",
        )
        self.slack.add_divider_block()

        for event in data:
            event_date = event.get("event_date")
            reason = event.get("reason")
            hours = event.get("hours")
            self.slack.add_section_block(
                text=f"Date: *{event_date}*\nReason: *{reason}*\nHours: *{hours}*"
            )
            self.slack.add_divider_block()
