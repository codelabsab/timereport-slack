import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict

from chalicelib.lib.api import (
    create_event,
    create_lock,
    delete_event,
    read_event,
    read_lock,
)
from chalicelib.lib.factory import factory
from chalicelib.lib.helpers import (
    check_locks,
    date_range,
    parse_date,
    validate_date,
    validate_reason,
)
from chalicelib.lib.list import get_list_data
from chalicelib.lib.period_data import get_period_data
from chalicelib.lib.reminder import remind_users
from chalicelib.lib.slack import (
    Slack,
    delete_message_menu,
    slack_client_responder,
    slack_responder,
    submit_message_menu,
)

log = logging.getLogger(__name__)


class Action:
    # Name to identify the action
    name = None
    # Help text to show when running `/timereport help`
    short_doc = None
    # Help text to show in help for specific command
    doc = None

    # Min arguments required
    min_arguments = 0

    # Max arguments required
    max_arguments = 100

    @staticmethod
    def create(payload, config):
        try:
            params = payload["text"].split()
        except KeyError:
            try:
                params = [payload["callback_id"]]
            except KeyError:
                log.info("No parameters received. Defaulting to help action")
                params = ["help"]

        action = params[0]

        for action_cls in Action.__subclasses__():
            if action_cls.name == action:
                return action_cls(payload, config)

        return UnsupportedAction(payload, config)

    def __init__(self, payload, config):
        self.payload = payload
        self.config = config
        self.payload = payload

        try:
            self.params = self.payload["text"].split()
        except KeyError:
            log.info("No parameters received. Defaulting to help action")
            self.params = ["help"]

        self.config = config
        self.bot_access_token = config["bot_access_token"]
        self.slack = Slack(slack_token=config["bot_access_token"])
        self.response_url = self.payload["response_url"]
        self.format_str = self.config.get("format_str")

        self.action = self.params[0]

        self.arguments = self.params[1:]

        try:
            self.user_id = self.payload["user_id"]
        except KeyError:
            self.user_id = self.payload["user"]["id"]
        try:
            self.user_name = self.payload["user_name"]
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

    def _get_events(self, date_str):
        return get_list_data(
            f"{self.config['backend_url']}", self.user_id, date_str=date_str
        )

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

    def is_valid(self):
        """
        Validate input data

        Optional. Only when some validation is required
        """
        if not (self.min_arguments <= len(self.arguments) <= self.max_arguments):
            self.send_response(
                message=f"Got the wrong number of arguments for {self.name}. See these examples: {self.doc}"
            )
            return False
        return True


class HelpAction(Action):
    name = "help"
    short_doc = "Provide this helpful output"
    doc = """
        Nothing to see here.. Try another action :)
        """

    def perform_action(self):
        msg = ""
        if len(self.arguments) > 0:
            for action_cls in Action.__subclasses__():
                if action_cls.name == self.arguments[0]:
                    msg = f"{action_cls.doc}"
                    break
        if msg == "":
            msg = "Supported actions are:\n"
            for action_cls in Action.__subclasses__():
                if action_cls == UnsupportedAction:
                    continue
                msg += f"\n{action_cls.name} - {action_cls.short_doc}"

        return self.send_response(message=msg)


class LockAction(Action):
    name = "lock"
    doc = """
        Lock the timereport for month

        create lock:
        /timereport lock 2019-08

        list locks:
        /timereport lock list 2020
        """
    short_doc = "Lock month to show you're done with the reporting"
    min_arguments = 1
    max_arguments = 2

    def perform_action(self):

        if self.arguments[0] == "list":
            return self._lock_list_action()

        if not validate_date(self.arguments[0], format_str="%Y-%m"):
            return self.send_response(
                message=f"Unable to lock using date '{self.arguments[0]}' :cry:"
            )
        log.debug(f"Event date is: {self.arguments[0]}")

        response = create_lock(
            url=self.config["backend_url"],
            user_id=self.user_id,
            date=self.arguments[0],
        )
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

        response = read_lock(url=self.config["backend_url"], user_id=self.user_id)
        locks = response.json()
        locks = [l for l in locks if l["event_date"].startswith(str(year))]

        if not locks:
            return self.send_response(f"No locks found for year *{year}*")

        self.slack.add_section_block(text=f"Locks found for months in *{year}*")
        self.slack.add_divider_block()

        for lock in locks:
            self.slack.add_section_block(text=f"{lock.get('event_date')} :lock:")

        self.slack.post_message(message="From timereport", channel=self.user_id)
        return ""


class AddAction(Action):
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
         * föräldraledig


        <day> can be
        "today" - Add event for todays date
        a date of the format "2020-03-10" or a range such as "2020-03-10:2020-03-17"

        <hours> can be:
        Nothing - Will default to a full workday
        Full hours (1, 2, 3 etc.)
        Partial hours (5.5 etc.) - `.5` = 30 minutes, `.25` = 15 minutes etc.
        """
    min_arguments = 2
    max_arguments = 3

    def perform_action(self):
        reason: str = self.arguments[0]
        input_date: str = self.arguments[1]
        hours: str = self.arguments[2] if len(self.arguments) == 3 else 8

        # validate reason
        if not validate_reason(self.config, reason):
            return self.send_response(message=f"Reason {reason} is not valid")

        # validate hours
        try:
            hours: float = float(hours)
        except ValueError:
            return self.send_response(message=f"Could not parse hours: {hours}")

        # validate dates
        parsed_dates: Dict[str, datetime] = parse_date(
            date=input_date, format_str=self.format_str
        )
        if parsed_dates["to"] is None or parsed_dates["from"] is None:
            return self.send_response(message=f"failed to parse date {input_date}")

        # validate months in date argument are not locked
        if check_locks(
            config=self.config,
            user_id=self.user_id,
            date=parsed_dates["from"],
            second_date=parsed_dates["to"],
        ):
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
            msg = "Added successfully"
            events = factory(self.payload, format_str=self.config.get("format_str"))
            response = create_event(
                url=self.config["backend_url"], event=json.dumps(events)
            )

            if response.status_code != 200:
                log.debug(
                    f"Event {events} got unexpected response from backend: {response.text}"
                )
                msg = "Failed to add one or more of the events"
            slack_responder(url=response_url, msg=msg)
            return ""
        else:
            slack_responder(url=response_url, msg="Action canceled :cry:")


class DeleteAction(Action):
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

        if check_locks(
            config=self.config,
            user_id=self.user_id,
            date=date["from"],
            second_date=date["to"],
        ):
            return self.send_response(
                message=f"Unable to delete since month is locked :cry:"
            )

        date_str = date["from"].strftime(self.format_str)
        events = self._get_events(date_str=date_str)
        has_events = any(
            event["event_date"] == date_str for event in json.loads(events)
        )
        if not has_events:
            return self.send_response(
                message=f"Unable to delete since no events found :cry:"
            )

        self.send_attachment(
            attachment=delete_message_menu(self.user_name, date_string)
        )
        return ""

    def perform_interactive(self):
        selection = self.payload.get("actions")[0].get("value")
        log.info(f"Selection is: {selection}")
        response_url = self.payload["response_url"]

        if selection == "submit_yes":
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
                deleted_count = int(delete_by_date.json().get("count", "0"))
                if deleted_count > 0:
                    msg = f"Deleted {deleted_count} events for {date}"
                else:
                    msg = f"No events found to delete for {date}"
                slack_responder(url=response_url, msg=msg)
            return ""
        else:
            slack_responder(url=response_url, msg="Action canceled :cry:")


class EditAction(Action):
    name = "edit"
    short_doc = "Edit a single event in timereport"
    doc = """
        Edit event in timereport for user.

        /timereport edit <reason> <date> <hours>

        Example: /timereport edit vab 2019-01-01 4
        """
    min_arguments = 3
    max_arguments = 3

    def perform_action(self):
        reason = self.arguments[0]

        if not validate_reason(self.config, reason):
            return self.send_response(message=f"Reason {reason} is not valid")

        date_input = self.arguments[1]

        try:
            hours = float(self.arguments[2])
        except ValueError as error:
            log.error(f"Failed to parse hours. Error was: {error}")
            return self.send_response(message="Could not parse hours")

        date: Dict[str, datetime] = parse_date(date_input, format_str=self.format_str)
        if date["from"] is None or date["to"] is None:
            return self.send_response(message=f"failed to parse date {date_input}")

        if date["from"] != date["to"]:
            return self.send_response(message=f"Edit doesn't support date range :cry:")

        if check_locks(
            config=self.config,
            user_id=self.user_id,
            date=date["from"],
            second_date=date["to"],
        ):
            return self.send_response(
                message=f"Can't edit date {date_input} because locked month :cry:"
            )
        event_to_edit = read_event(
            url=self.config["backend_url"],
            user_id=self.user_id,
            date={"from": date["from"].strftime(self.format_str)},
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


class UnsupportedAction(Action):
    name = "unsupported"

    def perform_action(self):
        return self.send_response(message=f"Unsupported action: {self.action}")


class ReminderAction(Action):
    name = "reminder"
    short_doc = "Run monthly lock reminder"
    doc = ""

    def perform_action(self):
        remind_users(
            self.slack, self.config["backend_url"], only_for_user_ids=[self.user_id]
        )


class ListAction(Action):
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
                message=f"Sorry, nothing to list with supplied argument {date_str}"
            )
            return ""

        self._create_list_message(data=list_data, period_data=period_data)
        self.slack.post_message(message="From timereport", channel=self.user_id)
        return ""

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
            hours = float(event.get("hours"))
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
