import os

from chalice import Chalice

from chalicelib.lib.slack import slack_payload_extractor, slack_responder
from chalicelib.lib.security import verify_token


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
    secret = os.getenv('signing_secret')
    if not verify_token(headers, request, secret):
        return 'Slack signing secret not valid'

    # extract slack payload from request and store some vars
    payload = slack_payload_extractor(request)
    response_url = payload["response_url"][0]

    try:
        commands = payload["text"][0].split()
        action = commands[0]
    except KeyError:
        # TODO:
        #  return help_menu()
        return help_menu(payload['user_id'])
    if action == "add":
        return "Not implemented"
        # TODO:  add(commands)

    if action == "edit":
        return "Not implemented"
        # TODO: return add(commands)

    if action == "delete":
        return "Not implemented"
        # TODO: delete(commands)

    if action == "list":
        return "Not implemented"
        # TODO: ls()

    if action == "lock":
        return "Not implemented"
        # TODO: lock(commands)

    if action == "help":
        help_menu(payload['user_id'])


def add():
    """
    Evaluate
    :return:
    """
    return NotImplemented


def delete():
    return NotImplemented


def ls():
    return NotImplemented


def lock():
    return NotImplemented


def help_menu(url, msg):
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



