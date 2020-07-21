import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict

from chalicelib.lib.add import post_event
from chalicelib.lib.api import read_event, read_lock, delete_event
from chalicelib.lib.factory import factory
from chalicelib.lib.helpers import date_range, parse_date
from chalicelib.lib.list import get_list_data
from chalicelib.lib.lock import lock_event
from chalicelib.lib.period_data import get_period_data
from chalicelib.lib.slack import (
    Slack,
    delete_message_menu,
    slack_client_responder,
    slack_responder,
    submit_message_menu,
)
from chalicelib.model.event import create_lock

log = logging.getLogger(__name__)


class BaseAction:
    # Name to identify the action
    name = None
    # Help text to show when running `/timereport help`
    short_doc = None

    def __init__(self, payload, config):
        self.payload = payload
        self.config = config
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

        self.action = self.params[0]

        self.arguments = self.params[1:]
        try:
            self.user_id = self.payload["user_id"][0]
        except KeyError:
            self.user_id = self.payload["user"]["id"]
        try:
            self.user_name = self.payload["user_name"][0]
        except KeyError:
            self.user_name = ""

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

    def _valid_reason(self, reason: str) -> bool:
        """
        Check that reason is valid
        """

        if reason in self.config.get("valid_reasons"):
            return True

        return False

    def _valid_number_of_args(self, min_args: int, max_args: int) -> bool:
        """
        Check that the number of arguments in the list is within the valid range
        """
        log.debug(f"Got {len(self.arguments)} number of args")
        if min_args <= len(self.arguments) <= max_args:
            return True
        return False

    def perform_action(self):
        """
        Run the action
        """
        raise NotImplementedError()

    def perform_interactive(self):
        """
        Run interactive slack callback

        Optional. Only for actions that require confirmation
        """
        raise NotImplementedError()


class HelpAction(BaseAction):
    name = "help"
    short_doc = "Provide this helpful output"
    doc = """
        Nothing to see here.. Try another action :)
        """

    def perform_action(self):
        msg = ""
        if len(self.arguments) > 0:
            for action_cls in BaseAction.__subclasses__():
                if action_cls.name == self.arguments[0]:
                    msg = f"{action_cls.doc}"
                    break
        if msg == "":
            msg = "Supported actions are:\n"
            for action_cls in BaseAction.__subclasses__():
                if action_cls == UnsupportedAction:
                    continue
                msg += f"\n{action_cls.name} - {action_cls.short_doc}"

        return self.send_response(message=msg)


class LockAction(BaseAction):
    name = "lock"
    doc = """
        Lock the timereport for month

        create lock:
        /timereport lock 2019-08

        list locks:
        /timereport lock list 2020
        """
    short_doc = "Lock month to show you're done with the reporting"

    def perform_action(self):
        if not self._valid_number_of_args(min_args=1, max_args=2):
            return self.send_response(
                message=f"Got the wrong number of arguments for {self.name}. See these examples: {self.doc}"
            )

        if self.arguments[0] == "list":
            return self._lock_list_action()

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

    def _lock_list_action(self) -> None:
        """
        Lists all locks for a given year
        """
        year = None

        try:
            year = int(self.arguments[1])
        except IndexError:
            now = datetime.now()
            year = now.year

        response = read_lock(
            url=self.config["backend_url"], user_id=self.user_id, date=year
        )
        locks = response.json()

        if not locks:
            return self.send_response(f"No locks found for year *{year}*")

        self.slack.add_section_block(text=f"Locks found for months in *{year}*")
        self.slack.add_divider_block()

        for lock in locks:
            self.slack.add_section_block(text=f"{lock.get('event_date')} :lock:")

        self.slack.post_message(message="From timereport", channel=self.user_id)
        return ""


class AddAction(BaseAction):
    name = "add"
    short_doc = "Add one or more events in timereport"
    doc = """
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

    def perform_action(self):
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

    def perform_interactive(self):
        selection = self.payload.get("actions")[0].get("value")
        log.info(f"Selection is: {selection}")
        response_url = self.payload["response_url"]

        if selection == "submit_yes":
            self.slack.ack_response(response_url=response_url)
            user_id = self.payload["user"]["id"]
            msg = "Added successfully"
            events = factory(self.payload, format_str=self.config.get("format_str"))
            failed_events = list()
            for event in events:
                response = post_event(
                    f"{self.config['backend_url']}/event/users/{user_id}",
                    json.dumps(event),
                )
                if response.status_code != 200:
                    log.debug(
                        f"Event {event} got unexpected response from backend: {response.text}"
                    )
                    failed_events.append(event.get("event_date"))

            if failed_events:
                log.debug(f"Got {len(failed_events)} events")
                msg = (
                    f"Successfully added {len(events) - len(failed_events)} events.\n"
                    f"These however failed: ```{failed_events} ```"
                )
            slack_responder(url=response_url, msg=msg)
            return ""
        else:
            slack_responder(url=response_url, msg="Action canceled :cry:")


class DeleteAction(BaseAction):
    name = "delete"
    doc = """
        Delete event in timereport.

        /timereport delete <date>

        Example: /timereport delete today
        """
    short_doc = "Delete event in timereport"

    def perform_action(self):
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
                attachment=delete_message_menu(self.user_name, date_string)
            )
        else:
            self.send_response(message=f"Unable to delete since month is locked :cry:")
        return ""

    def perform_interactive(self):
        selection = self.payload.get("actions")[0].get("value")
        log.info(f"Selection is: {selection}")
        response_url = self.payload["response_url"]

        if selection == "submit_yes":
            self.slack.ack_response(response_url=response_url)
            user_id = self.payload["user"]["id"]
            message = self.payload["original_message"]["attachments"][0]["fields"]
            date = message[1]["value"]
            if date == "today":
                date = datetime.now().strftime(self.config["format_str"])

            delete_by_date = delete_event(
                url=self.config["backend_url"], user_id=user_id, date=date
            )
            log.debug(f"Delete event posted. User={user_id}. Date={date}")

            if delete_by_date.status_code != 200:
                log.debug(
                    f"Error from backend: status code: {delete_by_date.status_code}. Response text: {delete_by_date.text}"
                )
                slack_responder(
                    url=response_url, msg=f"Got unexpected response from backend"
                )
            else:
                slack_responder(
                    url=response_url, msg=f"successfully deleted entry: {date}"
                )
            return ""
        else:
            slack_responder(url=response_url, msg="Action canceled :cry:")


class EditAction(BaseAction):
    name = "edit"
    short_doc = "Edit a single event in timereport"
    doc = """
        Edit event in timereport for user.

        /timereport edit <reason> <date> <hours>

        Example: /timereport edit vab 2019-01-01 4
        """

    def perform_action(self):

        if not self._valid_number_of_args(min_args=3, max_args=3):
            return self.send_response(message="Got the wrong number of arguments")

        reason = self.arguments[0]

        if not self._valid_reason(reason=reason):
            return self.send_response(message=f"Reason {reason} is not valid")

        date_input = self.arguments[1]

        try:
            hours = round(float(self.arguments[2]))
        except ValueError as error:
            log.error(f"Failed to parse hours. Error was: {error}")
            return self.send_response(message="Could not parse hours")

        date: Dict[str, datetime] = parse_date(date_input, format_str=self.format_str)
        if date["from"] is None or date["to"] is None:
            self.send_response(message="failed to parse date {date_string}")

        if date["from"] != date["to"]:
            return self.send_response(message=f"Edit doesn't support date range :cry:")

        if self._check_locks(date=date["from"], second_date=date["to"]):
            return self.send_response(
                message=f"Can't edit date {date_input} because locked month :cry:"
            )
        event_to_edit = read_event(
            url=self.config["backend_url"],
            user_id=self.user_id,
            date=date["from"].strftime(self.format_str),
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


class UnsupportedAction(BaseAction):
    name = "unsupported"

    def perform_action(self):
        return self.send_response(message=f"Unsupported action: {self.action}")


class ListAction(BaseAction):
    name = "list"
    doc = """
        List timereport for user.
        If no arguments supplied it will default to current month.
        Supported arguments:
        "today" - List the event for the todays date
        "date" - The date as a string.
        """
    short_doc = "List one or more events in timereport"

    def perform_action(self):
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

        period_data = get_period_data(date_str=date_str)
        list_data = self._get_events(date_str=date_str)

        if not list_data or list_data == "[]":
            log.debug(f"List returned nothing. Date string was: {date_str}")
            self.send_response(
                message=f"Sorry, nothing to list with supplied argument {arguments}"
            )
            return ""

        self._create_list_message(data=list_data, period_data=period_data)
        self.slack.post_message(message="From timereport", channel=self.user_id)
        return ""

    def _get_events(self, date_str):
        return get_list_data(
            f"{self.config['backend_url']}", self.user_id, date_str=date_str
        )

    def _create_list_message(self, data, period_data) -> None:
        """
        Create the slack block message layout for list action
        """
        data = json.loads(data)

        start_date = data[0].get("event_date")
        end_date = data[-1].get("event_date")

        self.slack.add_section_block(
            text=f"Reported time for period *{start_date}:{end_date}*",
        )
        self._show_period_data(list_data=data, period_data=period_data)
        self.slack.add_divider_block()

        for event in data:
            event_date = event.get("event_date")
            reason = event.get("reason")
            hours = event.get("hours")
            self.slack.add_section_block(
                text=f"Date: *{event_date}*\nReason: *{reason}*\nHours: *{hours}*"
            )
            self.slack.add_divider_block()

    def _show_period_data(self, list_data, period_data) -> Dict[str, int]:
        if not period_data:
            self.slack.add_section_block(text="No information about worked hours")
            return

        total_per_type = defaultdict(int)
        total_absent = 0
        for event in self._filter_non_workdays(list_data, period_data):
            hours = int(event.get("hours"))
            total_absent += hours
            total_per_type[event.get("reason")] += hours

        total_workhours = period_data["total_workdays"] * 8
        total_worked = total_workhours - total_absent

        self.slack.add_section_block(
            text=f"Total hours: {total_worked} / {total_workhours} ({-total_absent})"
        )

        for reason, hours in total_per_type.items():
            self.slack.add_section_block(text=f"{reason}: {hours}h")

    def _filter_non_workdays(self, list_data, period_data):
        holidays = [day["datum"] for day in period_data["holidays"]]

        workday_events = []
        for event in list_data:
            event_date = event.get("event_date")
            if event_date not in holidays and not self._is_weekend(event_date):
                workday_events.append(event)

        return workday_events

    def _is_weekend(self, date_str):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.isoweekday() >= 6


def create_action(payload, config):
    try:
        params = payload["text"][0].split()
    except KeyError:
        try:
            params = [payload["callback_id"]]
        except KeyError:
            log.info("No parameters received. Defaulting to help action")
            params = ["help"]

    action = params[0]

    for action_cls in BaseAction.__subclasses__():
        if action_cls.name == action:
            return action_cls(payload, config)

    return UnsupportedAction(payload, config)
