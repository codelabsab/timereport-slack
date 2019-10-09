import os

from chalice import Chalice

from chalicelib.lib.slack import slack_payload_extractor, slack_responder
from chalicelib.lib.security import verify_token
from chalicelib.lib import api
from dateutil.parser import parse


def command_handler(app: Chalice):
    """Takes chalice app, extracts headers and request
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
    """Checks if reason and date are valid strings
    If date is range ("2019-12-28:2020-01-03") it will
    test if range is valid
    :param payload: dict
        :type command:
            :param action: str "add"
            :param reason: str ["vab", "sick", "intern"]
            :param date: str ["2019-12-28", "today", "today 8", "today 24", "2019-12-28:2020-01-03"]
            :param hours: str: optional - hours is optional and defaults to 8 if not given

    Example data of command:
        command = "add vacation 2019-12-28:2020-01-03"
        command = "add sick today"
        command = "add vab 2019-12-28 4"
    """

    # extract text from slash command
    commands = payload['text'][0].split()

    # extract date or date range

    if not validate_reason(commands[1]):
        return "Not a valid reason"

    # validate hours
    try:
        if not validate_hours(commands[3]):
            return "Not valid hours"
    except IndexError:
        hours = 8

    # TODO: implement correct logic
    #      [] validate reason
    #      [] validate date and range
    #      [] validate hours

    r = api.create(
        url=os.getenv('backend_url'),
        event=event
    )
    if r.status_code != 200:
        return "fail!"


def delete(payload: dict):
    """Extracts user_id and date from payload and calls api.delete()"""
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
    """Extracts information from payload and calls api.lock()"""
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


def validate_reason(reason: str) -> bool:
    # TODO: should probably move to other lib
    """Validates a given reason for an event
    :param reason: str
    :return: bool
    """
    list_of_reasons: (
        "vab",
        "sick",
        "intern",
        "vacation",
    )
    if reason in list_of_reasons:
        return True
    else:
        return False


def validate_hours(hours: str) -> bool:
    # TODO: should probably move to other lib
    if round(float(hours)) > 8:
        return False
    elif round(float(hours)) < 0:
        return False
    else:
        return True
