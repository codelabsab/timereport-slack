import os
import botocore.vendored.requests.api as requests
from urllib.parse import parse_qs
import logging

log = logging.getLogger(__name__)

def slack_client_responder(token, channel_id, user_id, attachment):
    log.debug('we are now inside slack_client_responder')

    headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': f'Bearer {token}'}
    res = requests.post(url='https://slack.com/api/chat.postMessage',
                        json={'channel': channel_id, 'text': f'{user_id} from slack.py', 'attachments': attachment},
                        headers=headers
                        )
    log.debug(f'Response code is: {res.status_code}')
    log.debug(f'Url is: {res.url}')
    log.debug(f'function is slack_client_responder')
    if res.status_code == 200:
        log.debug(f'res.text is {res.text}')
        yield res.text
    else:
        return False, res.status_code

def slack_responder(url, msg):
    """
    Sends post to slack_response_url
    :param url: slack response_url
    :param msg:
    :return: boolean
    """
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=url, json={"text": msg}, headers=headers)
    if res.status_code == 200:
        return True
    else:
        return False


def slack_payload_extractor(req):
    """
    Extract the body data of the slack request.

    :param req: The request data from slack
    :return: dict
    """
    # parse_qs makes a list of all values, and that's why the v.pop() is necessary
    return {k: v.pop() for (k,v) in parse_qs(req).items()}


def verify_token(token):
    if token == os.getenv('slack_token'):
        return True
    else:
        return False


def verify_reasons(valid_reasons, reason):
    if reason in valid_reasons:
        return True
    else:
        return False


def verify_actions(valid_actions, action):
    if action in valid_actions:
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
            "fallback": "Submit these values?",
            "title": "Submit these values?",
            "callback_id": "submit",
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