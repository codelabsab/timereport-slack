import logging
import json
from chalicelib.lib.list import get_list_data
from chalicelib.lib.slack import (
    submit_message_menu,
    slack_client_responder,
    delete_message_menu,
    Slack,
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

    def perform_action(self):
        """
        Perform action.

        Supported actions are:
        add - Add new post in timereport
        edit - Not implemented yet
        delete - Delete post in timereport
        list - List posts in timereport
        lock - Not implemented yet
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

        if self.action == "lock":
            return self._lock_action()

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

        if not reason in self.config.get('valid_reasons'):
            message = f"Reason {reason} is not valid"
            log.debug(message)
            self.send_response(message=message)
            return ""

        self.date_start = events[0].get("event_date")
        self.date_end = events[-1].get("event_date")
        hours = events[0].get("hours")

        if self.check_lock_state():
            self.send_response(message="One or more of the events are locked")
            return ""

        self.send_attachment(attachment=submit_message_menu(
            user_name, reason, 
            self.date_start, self.date_end, hours)
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
            self.send_response(message=f"Got unexpected error with arguments: {arguments}")
            return ""
            
        log.debug(f"The date string set to: {date_str}")
        list_data = self._get_events(date_str=date_str)

        if not list_data or list_data == '[]':
            log.debug(f"List returned nothing. Date string was: {date_str}")
            self.send_response(message=f"Sorry, nothing to list with supplied argument {arguments}")
            return ""

        self.send_response(message=f"{list_data}")
        return ""

    def _delete_action(self):
        date = self.params[1]
        self.send_attachment(attachment=delete_message_menu(self.payload.get("user_name")[0], date))
        return ""

    def _edit_action(self):
        return self.send_response(message="Edit not implemented yet")


    def send_response(self, message):
        """
        Send a response to slack

        :message: The Message to send
        """
  
        log.debug("Sending message to slack")
        self.slack.client.chat_postMessage(
            channel=self.user_id,
            text=message,
        )
        return ""

    def send_attachment(self, attachment):
        """
        Send an message to slack using attachment
        :attachment: The attachment (slack specific attachment) to send
        """

        slack_client_response = slack_client_responder(
            token=self.bot_access_token,
            user_id=self.user_id,
            attachment=attachment,
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

    def check_lock_state(self):
        """
        Go through events and check if locked

        Return true if any locked events found
        """

        for event in json.loads(self._get_events(date_str=f"{self.date_start}:{self.date_end}")):
            if event.get("lock"):
                return True
        
        return False

    def _get_events(self, date_str):
        return get_list_data(
            f"{self.config['backend_url']}",
            self.user_id,
            date_str=date_str,
        )
    
    def _lock_action(self):
        """
        /timereport-dev lock 2019-08
        """
        event = create_lock(user_id=self.user_id, event_date=self.params[1])
        log.debug(f"lock event: {event}")
        response = lock_event(url=self.config['backend_url'], event=json.dumps(event))
        log.debug(f"response was: {response.text}")
        if response.status_code == 200:
            self.send_response(message=f"Lock successful! :lock: :+1:")
            return ""
        else:
            self.send_response(message=f"Lock failed! :cry:")
            return ""

