from chalice import Chalice
from chalicelib.lib.interactive import actions
from chalicelib.lib.slack import slack_payload_extractor, verify_token, slack_responder
from app import config
import logging


logger = logging.getLogger()
logger.setLevel(config["log_level"])


def interactive_handler(app: Chalice):
    """
    Route handler for /interactive session

    Parse request data and call action library functions in actions.py
    """

    # store backend url
    url: str = config["backend_url"]

    # store headers, request and secret
    headers = app.current_request.headers
    request = app.current_request.raw_body.decode()
    secret: str = config["signing_secret"]

    # verify validity of request
    if not verify_token(headers, request, secret):
        return "Slack signing secret not valid"

    # extract slack payload from request and store some vars
    payload: dict = slack_payload_extractor(request)
    submitted: str = payload.get("actions")[0].get("value")
    action: str = payload.get("callback_id")
    response_url: str = payload.get("response_url")

    if "yes" in submitted:
        if action is "add":
            results: list = actions.create_event(url=url, payload=payload)
            for result in results:
                if result.status_code is not 200:
                    slack_responder(url=response_url, msg=f"failed to create event")
                    logger.debug(f"failed to create event {result}")
                    return ""
            slack_responder(url=response_url, msg=f":white_check_mark:")
            return ""
        if action is "delete":
            results: list = actions.delete_event(url=url, payload=payload)
            for result in results:
                if result.status_code is not 200:
                    slack_responder(url=response_url, msg=f"failed to delete event")
                    logger.debug(f"failed to create event {result}")
                    return ""
            slack_responder(url=response_url, msg=f":white_check_mark:")
            return ""
    else:
        slack_responder(url=response_url, msg=f"cancelled :fire:")
        return ""
