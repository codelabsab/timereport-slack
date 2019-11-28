import logging
import json
from chalicelib.lib.list import get_list_data
from chalicelib.lib.api import read_lock, read_event
from chalicelib.lib.helpers import parse_date, date_range
from chalicelib.lib.slack import (
    submit_message_menu,
    slack_client_responder,
    delete_message_menu,
    slack_client_block_responder,
    Slack,
    create_block_message,
)
from chalicelib.lib.factory import factory
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
        """

        self.action = self.params[0]
        self.arguments = self.params[1:]
        self.user_id = self.payload["user_id"][0]
        self.user_name = self.payload["user_name"][0]

        log.debug(f"Action is: {self.action}")
        log.debug(f"Arguments are: {self.arguments}")
        if self.action == "add":
            return self._add_action()

        if self.action == "edit":
            return self._edit_action()

        if self.action == "delete":
            return self._delete_action()

        if self.action == "list":
            return self._list_action()

        if self.action == "lock":
            return self._lock_action()

        if self.action == "help":
            return self._help_action()

        return self._unsupported_action()

    def _unsupported_action(self):
        log.info(f"Action: {self.action} is not supported")
        return self.send_response(message=f"Unsupported action: {self.action}")

    def _add_action(self):

        # validate number of arguments
        if not self._valid_number_of_args(min_args=2, max_args=3):
            log.debug(f"args: {self.arguments}")
            return self.send_response(message="Wrong number of args for add command")

        # assign
        reason = self.arguments[0]
        input_dates = self.arguments[1]
        hours = self.arguments[2] if len(self.arguments) == 3 else 8

        # validate reason
        if not self._valid_reason(reason=reason):
            return self.send_response(message=f"Reason {reason} is not valid")

        # validate hours
        try:
            hours = round(float(hours))
        except ValueError:
            return self.send_response(message="Could not parse hours")

        # validate dates
        parsed_dates: list = parse_date(date=input_dates, format_str=self.format_str)
        if not parsed_dates:
            self.send_response(message="failed to parse date {date}")

        # store from and to
        parsed_date_from: datetime = parsed_dates[0]
        parsed_date_to: datetime = parsed_dates[1] if len(
            parsed_dates
        ) > 1 else parsed_dates[0]

        # validate months in date argument are not locked
        if self._check_locks(date=parsed_date_from, second_date=parsed_date_to):
            return self.send_response(
                message=f"Unable to add since one or more month in range are locked :cry:"
            )

        # all validation completed successfully - send interactive menu with dates in correct format
        date_from: str = parsed_date_from.strftime(self.format_str)
        date_to: str = parsed_date_to.strftime(self.format_str)
        self.send_attachment(
            attachment=submit_message_menu(
                user_name=self.user_name,
                reason=reason,
                date=f"{date_from}:{date_to}",
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
        self.send_block(message=list_data)
        return ""

    def _delete_action(self):

        date_string = self.params[1]
        date = parse_date(date_string, format_str=self.format_str)

        if not date:
            return self.send_response(message=f"Could not parse date {date_string}")

        if len(date) > 1:
            return self.send_response(
                message=f"Delete doesn't support date range :cry:"
            )

        if not self._check_locks(date=date[0], second_date=date[0]):
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

        date = parse_date(date_input, format_str=self.format_str)
        if not date:
            self.send_response(message="failed to parse date {date_string}")

        if len(date) > 1:
            return self.send_response(message=f"Edit doesn't support date range :cry:")

        if self._check_locks(date=date[0], second_date=date[0]):
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

    def send_block(self, message):
        """
        Send a response to slack using blocks and WEB API
        :message: The message is a list of dicts

        [{"user_id": "U2FGC795G", "hours": "8", "user_name": "kamger", "event_date": "2019-08-30", "reason": "intern_arbete"}]

        """
        # will generate a block object
        block = create_block_message(json.loads(message))

        slack_client_response = slack_client_block_responder(
            token=self.bot_access_token, user_id=self.user_id, block=block
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
        return self.send_response(message=f"{self.perform_action.__doc__}")

    def _get_events(self, date_str):
        return get_list_data(
            f"{self.config['backend_url']}", self.user_id, date_str=date_str
        )

    def _lock_action(self):
        """
        /timereport-dev lock 2019-08
        """
        event = create_lock(user_id=self.user_id, event_date=self.params[1])
        log.debug(f"lock event: {event}")
        response = lock_event(url=self.config["backend_url"], event=json.dumps(event))
        log.debug(f"response was: {response.text}")
        if response.status_code == 200:
            self.send_response(message=f"Lock successful! :lock: :+1:")
            return ""
        else:
            self.send_response(message=f"Lock failed! :cry:")
            return ""

    def _check_locks(self, date: datetime, second_date: datetime) -> bool:
        """
        Check dates for lock.
        """
        is_locked = False
        dates_to_check = list()
        for date in date_range(start_date=date, stop_date=second_date):
            if not date.strftime("%Y-%m") in dates_to_check:
                dates_to_check.append(date.strftime("%Y-%m"))

        log.debug(f"Got {len(dates_to_check)} date(s) to check")
        for date in dates_to_check:
            respone = read_lock(
                url=self.config["backend_url"], user_id=self.user_id, date=date
            )
            if respone.json():
                log.info(f"Date {date} is locked")
                is_locked = True

        return is_locked

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
