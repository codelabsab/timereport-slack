import logging
from chalicelib.lib.list import get_list_data
from chalicelib.lib.slack import (
    slack_responder,
    submit_message_menu,
    slack_client_responder,
    delete_message_menu,
)
from chalicelib.lib.factory import factory

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
        self.response_url = self.payload["response_url"][0]

    def perform_action(self):
        """
        Perform action.

        Supported actions are:
        add - Add new post in timereport
        edit - Not implemented yet
        delete - Delete post in timereport
        list - List posts in timereport
        help - Provide this helpful output
        """

        self.action = self.params[0]
        log.debug(f"Action is: {self.action}")
        self.user_id = self.payload["user_id"][0]

        if self.action == "add":
            return self._add_action()

        if self.action == "edit":
            return self._edit_action()

        if self.action == "delete":
            return self._delete_action()

        if self.action == "list":
            return self._list_action()

        if self.action == "help":
            return self._help_action()

        return self._unsupported_action()

    def _unsupported_action(self):
        log.info(f"Action: {self.action} is not supported")
        return self.send_response(message=f"Unsupported action: {self.action}")

    def _add_action(self):
        events = factory(self.payload)
        if not events:
            return self.send_response(message="Wrong arguments for add command")

        log.info(f"Events is: {events}")
        user_name = events[0].get("user_name")[0]
        reason = events[0].get("reason")
        date_start = events[0].get("event_date")
        date_end = events[-1].get("event_date")
        hours = events[0].get("hours")
        self.attachment = submit_message_menu(
            user_name, reason, date_start, date_end, hours
        )
        log.info(f"Attachment is: {self.attachment}")
        self.send_response()
        return ""

    def _list_action(self):
        """
        List timereport for user.
        If no arguments supplied it will default to all.

        Supported arguments:
        "today" - Not implemented yet
        "date" - The date as a string. Use ":" as delimiter for two dates: "2019-01-01:2019-01-02"
        """

        default_date_str = "all"
        arguments = self.params[1:]

        if not arguments:
            log.debug(
                f"No arguments for list. Setting default value: {default_date_str}"
            )
            arguments = [default_date_str]

        if arguments[0] == "today":
            self.send_response(message="Today argument not implemented yet")
            return ""

        list_data = get_list_data(
            f"{self.config['backend_url']}",
            self.user_id,
            # We don't validate the input, just take the last argument recieved.
            date_str=arguments[0],
        )
        if not list_data:
            log.debug(f"List returned nothing. Event date was: {date_str}")
            self.send_response(message=f"Sorry, nothing to list for date {date_str}")
            return ""

        self.send_response(message=f"```{list_data}```")
        return ""

    def _delete_action(self):
        date = self.params[1]
        self.attachment = delete_message_menu(self.payload.get("user_name")[0], date)
        log.debug(
            f"Attachment is: {self.attachment}. user_name is {self.payload.get('user_name')[0]}"
        )
        self.send_response()
        return ""

    def _edit_action(self):
        return self.send_response(message="Edit not implemented yet")

    def send_response(self, message=False):
        """
        Send a response to slack

        If param message is False the attribute self.attachment is excpected
        to exist.
        """
        if message:
            slack_responder(url=self.response_url, msg=message)
            return ""

        slack_client_response = slack_client_responder(
            token=self.bot_access_token,
            user_id=self.user_id,
            attachment=self.attachment,
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
