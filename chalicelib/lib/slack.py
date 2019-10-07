import os
import botocore.vendored.requests.api as requests
from urllib.parse import parse_qs
import logging
import json
import slack

log = logging.getLogger(__name__)


class Slack:

    def __init__(self, slack_token):
        self.slack_token = slack_token
        self.client = slack.WebClient(token=slack_token)


def slack_client_responder(token, user_id, attachment, url='https://slack.com/api/chat.postMessage'):
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
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': f'Bearer {token}'}
    return requests.post(
        url=url,
        json={'channel': user_id, 'text': 'From timereport', 'attachments': attachment},
        headers=headers
    )


def slack_responder(url, msg):
    """
    Sends post to slack_response_url
    :param url: slack response_url
    :param msg:
    :return: boolean
    """
    headers = {'Content-Type': 'application/json'}
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
        extracted_data = json.loads(data.get('payload')[0])
        log.info(f'Extracted data: {extracted_data}')
        return extracted_data

    if data.get('command'):
        return data
    else:
        return "failed extracting payload", 200


def verify_reasons(valid_reasons, reason):
    if reason in valid_reasons:
        return True
    else:
        return False


def submit_message_menu(user_name, reason, date_start, date_end, hours):
    attachment = [
        {
            "fields": [
                {
                    "title": "User",
                    "value": user_name
                },

                {
                    "title": "Type",
                    "value": reason
                },
                {
                    "title": "Date start",
                    "value": date_start
                },
                {
                    "title": "Date end",
                    "value": date_end
                },

                {
                    "title": "Hours",
                    "value": hours
                }
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
                    "value": "submit_yes"
                },
                {
                    "name": "no",
                    "text": "No",
                    "type": "button",
                    "style": "danger",
                    "value": "submit_no"
                }
            ]
        }
    ]
    return attachment


def delete_message_menu(user_name, date):
    attachment = [
        {
            "fields": [
                {
                    "title": "User",
                    "value": user_name
                },
                {
                    "title": "Date",
                    "value": date
                }
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
                    "value": "submit_yes"
                },
                {
                    "name": "no",
                    "text": "No",
                    "type": "button",
                    "style": "danger",
                    "value": "submit_no"
                }
            ]
        }
    ]
    return attachment