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
