from chalice import Chalice
from chalicelib.lib.interactive.actions import interactive_add, interactive_delete
from chalicelib.lib.slack import slack_payload_extractor
from chalicelib.lib.security import verify_token
from app import config


def interactive_handler(app: Chalice):
    """
    Extracts data from request and checks if
    users wants to submit or not.

    Routes payload data to correct function that
    mangles data to be sent before sending to backend api
    """

    # store backend url
    url = config["backend_url"]

    # store headers, request and secret
    headers = app.current_request.headers
    request = app.current_request.raw_body.decode()
    # TODO: this should we a str: SECRET in app.py instead
    secret: str = config["signing_secret"]

    # verify validity of request
    if not verify_token(headers, request, secret):
        return "Slack signing secret not valid"

    # extract slack payload from request and store some vars
    payload = slack_payload_extractor(request)
    submit = payload.get("actions")[0].get("value")
    action = payload.get("callback_id")

    # did user press yes?
    if submit == "submit_yes":
        # is the action add?
        if action == "add":
            # send fields to add function for further processing and before call to api lib
            results = interactive_add(url=url, payload=payload)
            for result in results:
                if result.status_code != 200:
                    # TODO: slack_client_block_responder("failed")
                    return ""
            # TODO: slack_client_block_responder("success")?
            return ""
        # or is the action delete?
        if action == "delete":
            results = interactive_delete(url=url, payload=payload)
            for result in results:
                if result.status_code != 200:
                    # TODO: slack_client_block_responder("failed")
                    return ""
            # TODO: slack_client_block_responder("failed")
            return ""

    # user pressed no
    else:
        # TODO: slack_client_block_responder("cancelled")
        return ""
