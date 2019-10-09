import os

from chalice import Chalice

from chalicelib.lib.slack import slack_payload_extractor, slack_responder
from chalicelib.lib.security import verify_token
from chalicelib.lib import api
from dateutil.parser import parse


def command_handler(app: Chalice):
    """
    Takes chalice app, extracts headers and request
    validates token and sends extracted data
    to the correct function handler
    """
    # store headers and request
    headers = app.current_request.headers
    request = app.current_request.raw_body.decode()

    # verify validity of request
    secret: str = os.getenv('signing_secret')
    if not verify_token(headers, request, secret):
        return 'Slack signing secret not valid'

    # extract slack payload from request and store some vars
    payload: dict = slack_payload_extractor(request)
    # TODO: response_url = payload["response_url"][0] ???

    try:
        action: str = payload["text"][0].split()[0]
    except KeyError:
        return help_menu(payload['user_id'])

    if action == "add":
        return add(payload)

    if action == "edit":
        return "Not implemented"
        # TODO: Should this even exist?

    if action == "delete":
        return delete(payload)

    if action == "list":
        return "Not implemented"
        # TODO: ls()

    if action == "lock":
        lock(payload)

    if action == "help":
        help_menu(payload['user_id'])


def add(payload: dict):
    """
    :return:
    """
    return NotImplemented


def delete(payload: dict):
    date: str = payload['text'][0].split()[-1]
    if parse(date, fuzzy=False):
        r = api.delete(
            url=os.getenv('backend_url'),
            date=date,
            user_id=payload['user_id'][0],
        )
        if r.status_code != 200:
            return f"Could not lock {date}"
    else:
        return f"Could not parse {date}"
    return f"{date} has been deleted"


def ls(payload: dict):
    return NotImplemented


def lock(payload: dict):
    # store date
    date: str = payload['text'][0].split()[-1]
    # check if date is valid
    if parse(date, fuzzy=False):
        # TODO: Use config dict to get backend_url?
        r = api.lock(
            url=os.getenv('backend_url'),
            user_id=payload['user_id'][0],
            date=date
        )
        if r.status_code != 200:
            return f"Could not lock {date}"
    else:
        return f"Could not parse {date}"
    return f"{date} has been locked"


def help_menu(url: str):
    msg = """
        Perform action.

        Supported actions are:
        add - Add new post in timereport
        edit - Not implemented yet
        delete - Delete post in timereport
        list - List posts in timereport
        lock - Not implemented yet
        help - Provide this helpful output
        """
    slack_responder(url=url, msg=msg)
    return ""
