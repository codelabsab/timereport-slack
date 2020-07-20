import base64
import hashlib
import hmac
import json
import logging
import os
from urllib.parse import parse_qs

import requests

log = logging.getLogger(__name__)


class Slack:

    slack_api_url = "https://slack.com/api"

    def __init__(self, slack_token):
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {slack_token}",
        }
        self.blocks = list()

    def post_message(
        self, message: str, channel: str, as_user=None
    ) -> requests.models.Response:
        """
        Send slack message to channel. Channel can be a slack user ID to send direct message
        :param message: The text to send
        :param channel: The channel to send the message
        :param as_user: When using user_id as channel, set to false for the message to go only to that user
        :return: requests.models.Response
        """

        data = {"channel": channel, "text": message}
        if as_user is not None:
            data["as_user"] = as_user

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
            if not response.text == "ok" and response.status_code == 200:
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

    def add_divider_block(self, slack_block_id: str = "") -> None:
        """
        Add a slack block divider to the blocks attribute
        https://api.slack.com/reference/block-kit/blocks#divider
        """
        self.blocks.append({"type": "divider", "block_id": slack_block_id})

    def add_section_block(self, text: str) -> None:
        """
        Add a slack section block to the blocks attribute
        https://api.slack.com/reference/block-kit/blocks#section
        """
        self.blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": text}}
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
