import os
import botocore.vendored.requests.api as requests
from urllib.parse import parse_qs


def slack_responder(url, msg):
    """
    Sends post to slack_response_url
    :param url: slack response_url
    :param msg:
    :return: boolean
    """
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=url, data={"text": f"{msg}"}, headers=headers)
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
    """
    Verify token
    :param token: The token from the request
    :return: boolean
    """
    if token == os.environ.get('SLACK_TOKEN'):
        return True
    else:
        return False
