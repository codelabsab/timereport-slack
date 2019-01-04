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
    return {k: v.pop() for (k,v) in parse_qs(req['body']).items()}


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
