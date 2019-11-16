import logging
import json
from chalicelib.lib.list import get_list_data
from chalicelib.lib.api import read_lock
from chalicelib.lib.helpers import parse_date, get_dates
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
        log.debug(f"Action is: {self.action}")
        self.user_id = self.payload["user_id"][0]
        self.user_name = self.payload["user_name"][0]

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

        if len(self.params) < 3 or len(self.params) > 4:
            log.debug(f"params: {self.params}")
            return self.send_response(message="Wrong number of args for add command")

        reason = self.params[1]
        date = self.params[2]
        hours = 8
        if len(self.params) == 4:
            try:
                hours = round(float(self.params[3]))
            except ValueError:
                return self.send_response(message="Could not parse hours")

        if reason not in self.config.get("valid_reasons"):
            message = f"Reason {reason} is not valid"
            log.debug(message)
            self.send_response(message=message)
            return ""

        date = parse_date(date=date, format_str=self.format_str)

        if not date:
            self.send_response(message="failed to parse date")

        self.send_attachment(
            attachment=submit_message_menu(self.user_name, reason, ":".join(date.keys()), hours)
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

        if len(date.keys()) > 1:
            return self.send_response(message=f"Delete doesn't support date range :cry:")

        dates_to_check = get_dates(first_date=date.get(date_string))
        if not dates_to_check:
            return self.send_response(message=f"No dates to check for locks :cry:")

        if not self._check_locks(dates=dates_to_check):
            self.send_attachment(
                attachment=delete_message_menu(self.payload.get("user_name")[0], date_string)
            )
        else:
            self.send_response(message=f"Unable to delete since month is locked :cry:")
        return ""

    def _edit_action(self):
        """
        Edit event in timereport for user.
        If no arguments supplied it will try to edit today.
        """

        date = datetime.now().strftime("%Y-%m-%d")

        try:
            if self.params[1] != "today":
                date = self.params[1]
        except IndexError:
            log.debug(f"Didn't get any params. Setting date to {date}")

        event_to_edit = None
        try:
            event_to_edit = json.loads(self._get_events(date_str=date))
        except json.decoder.JSONDecodeError as error:
            log.error(f"Unable to decode JSON. Error was: {error}")
            self.send_response(
                message=f"Something went wrong fetching event to edit. :cry:"
            )
            return ""

        log.debug(f"Event to edit is: {event_to_edit}")
        if not event_to_edit:
            self.send_response(message=f"No event for date {date} to edit. :shrug:")
            return ""

        self.send_response(
            message=f"Found event to edit, but I can't do that yet, sorry. :cry:"
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


    def _check_locks(self, dates: list) -> bool:
        """
        Go through the list of dates and check if locked
        """
        is_locked = False
        for date in dates:
            respone = read_lock(
                url=self.config["backend_url"], user_id=self.user_id, date=date
            )
            if respone.json():
                is_locked = True

        return is_locked