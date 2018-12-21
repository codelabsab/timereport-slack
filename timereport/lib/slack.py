import os
import botocore.vendored.requests.api as requests


def slack_responder(url, msg):
    '''
    Sends post to slack_response_url
    :param url: slack response_url
    :param msg:
    :return: True
    '''
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=url, data={"text": f"{msg}"}, headers=headers)
    if res.status_code == 200:
        return True
    else:
        return False


def slack_payload_extractor(req):
    '''
    Returns a dict containing the pure slack payload. Removes apigw metadata.
    d =
     "token": "secret",
     "team_id": "team_id",
     "team_domain": "team_domain",
     "channel_id": "channel_id",
     "channel_name": "channel_name",
     "user_id": "user101",
     "user_name": "test_user",
     "command": "%2Fno-wsgi",
     "text": "add+vab+2018-10-01:2018-10-10",
     "response_url": "https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F4913463461%2FbVUlrKZrnElSOBUqn01FoxNf",
     "trigger_id": "490225208629.83549292471.860541eab9e9c3c6d2234ea2e222c7a5"
    '''
    d = {}
    for param in req['body'].split("&"):
        key, value = param.split("=")
        d[key] = value
    return d


def verify_token(token):
    if token == os.environ['SLACK_TOKEN']:
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
