import os
import requests
from urllib.parse import parse_qs
import logging
import json
import hmac
import hashlib
import base64

log = logging.getLogger(__name__)


class Slack:

    slack_api_url = "https://slack.com/api"

    def __init__(self, slack_token):
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {slack_token}",
        }
        self.blocks = list()

    def post_message(self, message: str, channel: str) -> requests.models.Response:
        """
        Send slack message to channel. Channel can be a slack user ID to send direct message
        :param message: The text to send
        :param channel: The channel to send the message
        :return: requests.models.Response
        """

        data = {"channel": channel, "text": message}

        data["blocks"] = self.blocks if self.blocks else None
        log.debug(f"Data is: ${data}")

        return self._handle_response(
            requests.post(
                url=f"{self.slack_api_url}/chat.postMessage",
                json=data,
                headers=self.headers,
            )
        )

    def _handle_response(
        self, response: requests.models.Response
    ) -> requests.models.Response:
        """
        Check the response from slack.
        A normal slack response should always be JSON with a key "ok" with value True for the response to be valid

        """
        try:
            validated_response = response.json()
            if not validated_response.get("ok"):
                log.critical(
                    f"Slack responded with not ok. Message was: {validated_response}"
                )
        except (AttributeError, ValueError) as error:
            log.critical(
                f"Unable get valid json from response. Error was: {error}",
                exc_info=True,
            )

        return response

    def ack_response(self, response_url):
        """
        Send acknowledge response.
        This is required by slack for interactive messages.
        See https://api.slack.com/messaging/interactivity#responding_to_interactions
        """
        log.debug(f"Sending ack message to slack response URL: {response_url}")
        return self._handle_response(
            requests.post(
                url=response_url,
                headers={"Content-Type": "application/json"},
                json={"text": "OK, hang on when I do this!"},
            )
        )


def slack_client_responder(
    token, user_id, attachment, url="https://slack.com/api/chat.postMessage"
):
    """
    Sends an direct message to a user.
    https://api.slack.com/methods/chat.postEphemeral

    :param token: slack token
    :param user_id: The user id
    :param attachment: The slack attachment
    :param url: The slack URL
    :return: request response object
    """

    log.debug(f"Will try to post direct message to user {user_id}")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}",
    }
    return requests.post(
        url=url,
        json={"channel": user_id, "text": "From timereport", "attachments": attachment},
        headers=headers,
    )


def slack_responder(url, msg):
    """
    Sends post to slack_response_url
    :param url: slack response_url
    :param msg:
    :return: boolean
    """
    headers = {"Content-Type": "application/json"}
    res = requests.post(url=url, json={"text": msg}, headers=headers)
    return res.status_code


def slack_payload_extractor(req):
    """
    Extract the body data of the slack request.

    :param req: The request data from slack
    :return: dict
    """
    data = parse_qs(req)

    log.debug(f"data is: {data}")

    if data.get("payload"):
        extracted_data = json.loads(data.get("payload")[0])
        log.info(f"Extracted data: {extracted_data}")
        return extracted_data

    if data.get("command"):
        return data
    else:
        return "failed extracting payload", 200


def verify_token(headers, body, signing_secret):
    """
    https://api.slack.com/docs/verifying-requests-from-slack

    1. Grab timestamp and slack signature from headers.
    2. Concat and create a signature with timestamp + body
    3. Hash the signature together with your signing_secret token from slack settings
    4. Compare digest to slack signature from header
    """
    request_timestamp = headers["X-Slack-Request-Timestamp"]
    slack_signature = headers["X-Slack-Signature"]

    request_basestring = f"v0:{request_timestamp}:{body}"
    my_sig = f'v0={hmac.new(bytes(signing_secret, "utf-8"), bytes(request_basestring, "utf-8"), hashlib.sha256).hexdigest()}'

    if hmac.compare_digest(my_sig, slack_signature):
        return True
    else:
        return False


def submit_message_menu(user_name, reason, date, hours):
    attachment = [
        {
            "fields": [
                {"title": "User", "value": user_name},
                {"title": "Type", "value": reason},
                {"title": "Date", "value": date},
                {"title": "Hours", "value": hours},
            ],
            "footer": "Code Labs timereport",
            "footer_icon": "https://codelabs.se/favicon.ico",
            "fallback": "Submit these values to database?",
            "title": "Submit these values to database?",
            "callback_id": "add",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "submit",
                    "text": "submit",
                    "type": "button",
                    "style": "primary",
                    "value": "submit_yes",
                },
                {
                    "name": "no",
                    "text": "No",
                    "type": "button",
                    "style": "danger",
                    "value": "submit_no",
                },
            ],
        }
    ]
    return attachment


def delete_message_menu(user_name, date):
    attachment = [
        {
            "fields": [
                {"title": "User", "value": user_name},
                {"title": "Date", "value": date},
            ],
            "footer": "Code Labs timereport",
            "footer_icon": "https://codelabs.se/favicon.ico",
            "fallback": "Delete these values from database?",
            "title": "Delete these values from database?",
            "callback_id": "delete",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "submit",
                    "text": "submit",
                    "type": "button",
                    "style": "primary",
                    "value": "submit_yes",
                },
                {
                    "name": "no",
                    "text": "No",
                    "type": "button",
                    "style": "danger",
                    "value": "submit_no",
                },
            ],
        }
    ]
    return attachment


def create_block_message(message: dict) -> list:
    """

    :param message: a list of dicts
    :return: block object list of dicts
    """
    # [{"user_id": "U2FGC795G", "hours": "8", "user_name": "kamger", "event_date": "2019-08-30", "reason": "intern_arbete"}]

    start_date = message[0].get("event_date")
    end_date = message[-1].get("event_date")

    block_header_section = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Reported time for period *{start_date}:{end_date}*",
        },
    }

    block_divider = {"type": "divider"}

    block = [block_header_section, block_divider]

    for entry in message:
        start_date = entry.get("event_date")
        reason = entry.get("reason")
        hours = entry.get("hours")

        block_entry = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Date: *{start_date}*\nReason: *{reason}*\nHours: *{hours}*",
            },
        }
        block.append(block_entry)
        block.append(block_divider)

    return block
