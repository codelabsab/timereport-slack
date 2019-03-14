import logging
from chalicelib.lib.list import get_between_date, get_user_by_id
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
        self.params = self.payload["text"][0].split()
        self.config = config
        self.slack_token = config["slack_token"]
        self.response_url = self.payload["response_url"][0]

    def perform_action(self):
        self.action = self.params[0]
        self.user_id = self.payload["user_id"][0]

        if self.action == "add":
            return self._add_action()

        if self.action == "edit":
            return self._edit_action()

        if self.action == "delete":
            return self._delete_action()

        if self.action == "list":
            return self._list_action()

        return self._unsupported_action()

    def _unsupported_action(self):
        slack_responder(self.response_url, f"Unsupported action: {self.action}")
        return ""

    def _add_action(self):
        events = factory(self.payload)
        if not events:
            return slack_responder(
                self.payload["response_url"], "Wrong arguments for add command"
            )

        log.info(f"Events is: {events}")
        user_name = events[0].get("user_name")[0]
        reason = events[0].get("reason")
        date_start = events[0].get("event_date")
        date_end = events[-1].get("event_date")
        hours = events[0].get("hours")
        # create attachment with above values for submit button
        attachment = submit_message_menu(user_name, reason, date_start, date_end, hours)
        log.info(f"Attachment is: {attachment}")

        slack_client_response = slack_client_responder(
            token=self.slack_token, user_id=self.user_id, attachment=attachment
        )

        if slack_client_response.status_code != 200:
            log.error(
                f"""Failed to send response to slack. Status code was: {slack_client_response.status_code}.
                The response from slack was: {slack_client_response.text}"""
            )
            return "Slack response to user failed"
        else:
            log.debug(f"Slack client response was: {slack_client_response.text}")

        return ""

    def _list_action(self):
        get_by_user = get_user_by_id(f"{self.config['backend_url']}/user", self.user_id)
        if isinstance(get_by_user, tuple):
            log.debug(f"Failed to return anything: {get_by_user[1]}")
        else:
            for r in get_by_user:
                slack_responder(self.response_url, f"```{str(r)}```")

        event_date = "".join(self.params[-1:])
        if ":" in event_date:
            # temporary solution

            start_date, end_date = event_date.split(":")

            get_by_date = get_between_date(
                f"{self.config['backend_url']}/user/{self.user_id}",
                start_date,
                end_date,
            )

            for r in get_by_date:
                slack_responder(self.response_url, f"```{str(r)}```")

        return ""

    def _delete_action(self):
        date = self.params[1]
        attachment = delete_message_menu(self.payload.get("user_name")[0], date)
        log.debug(
            f"Attachment is: {attachment}. user_name is {self.payload.get('user_name')[0]}"
        )

        slack_client_response = slack_client_responder(
            token=self.slack_token, user_id=self.user_id, attachment=attachment
        )
        if slack_client_response.status_code != 200:
            log.error(
                f"""Failed to send response to slack. Status code was: {slack_client_response.status_code}.
                The response from slack was: {slack_client_response.text}"""
            )
            return "Slack response to user failed"
        else:
            log.debug(f"Slack client response was: {slack_client_response.text}")

    def _edit_action(self):
        slack_responder(self.response_url, "Edit not implemented yet")
        return ""

