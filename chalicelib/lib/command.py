import os

from chalice import Chalice

from app import TOKEN, SECRET, REASONS, API_URL
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
    if not verify_token(headers, request, SECRET):
        return 'Slack signing secret not valid'

    # extract payload from request
    payload: dict = slack_payload_extractor(request)

    try:
        cmd: list = payload["text"][0].split()
        user_id = payload["user_id"][0]
        action: str = cmd[0]
    except KeyError:
        return help_menu(url=payload["response_url"][0])

    if action == "add":
        return add(cmd, user_id)

    # TODO: should this exist?
    # if action == "edit":
    #     return "Not implemented"

    if action == "delete":
        return delete(cmd, user_id)

    if action == "list":
        return ls(cmd, user_id)

    if action == "lock":
        lock(cmd, user_id)

    if action == "help":
        help_menu(url=payload["response_url"][0])


def add(cmd: list, user_id: str):
    """Checks if reason and date are valid strings
    If date is range ("2019-12-28:2020-01-03") it will
    test if range is valid
    :param cmd: list containing:
        cmd[0] = action: str "add"
        cmd[1] = reason: str ["vab", "sick", "intern"]
        cmd[2] = date: str ["2019-12-28", "today", "today 8", "today 24", "2019-12-28:2020-01-03"]
        cmd[3] = hours: OPTIONAL str: - hours is optional and defaults to 8 if not given
    :param user_id: str: user_id

    Example data of command:
        command = "add vacation 2019-12-28:2020-01-03"
        command = "add sick today"
        command = "add vab 2019-12-28 4"
    """

    # validate reason
    if not validate_reason(cmd[1]):
        return "Not a valid reason"

    # validate hours
    try:
        if not validate_hours(cmd[3]):
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


def delete(cmd: list, user_id: str):
    """Extracts user_id and date from payload and calls api.delete()"""
    date: str = cmd[-1]
    if parse(date, fuzzy=False):
        r = api.delete(
            url=os.getenv('backend_url'),
            date=date,
            user_id=user_id,
        )
        if r.status_code != 200:
            return f"Could not lock {date}"
    else:
        return f"Could not parse {date}"
    return f"{date} has been deleted"


def ls(cmd: list, user_id: str):
    """Implements api.read() and Retrieves events for a range or defaults to current month"""


def lock(cmd: list, user_id: str):
    """Extracts information from payload and calls api.lock()"""

    # store date
    date: str = cmd[-1]

    # check if date is valid
    if parse(date, fuzzy=False):

        r = api.lock(
            url=API_URL,
            user_id=user_id,
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
    if reason in REASONS:
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
