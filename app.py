import logging
import os

from chalice import Chalice

from chalicelib.action import create_action
from chalicelib.lib.helpers import parse_config
from chalicelib.lib.reminder import remind_users
from chalicelib.lib.slack import (
    Slack,
    slack_client_responder,
    slack_payload_extractor,
    slack_responder,
    submit_message_menu,
    verify_token,
)

app = Chalice(app_name="timereport")
app.debug = True


logger = logging.getLogger()

dir_path = os.path.dirname(os.path.realpath(__file__))
config = parse_config(f"{dir_path}/chalicelib/config.yaml")
config["backend_url"] = os.getenv("backend_url")
config["bot_access_token"] = os.getenv("bot_access_token")
config["signing_secret"] = os.getenv("signing_secret")
config["enable_lock_reminder"] = os.getenv("enable_lock_reminder")
config["format_str"] = "%Y-%m-%d"

logger.setLevel(config["log_level"])


@app.route(
    "/interactive",
    methods=["POST"],
    content_types=["application/x-www-form-urlencoded"],
)
def interactive():
    try:
        req = app.current_request.raw_body.decode()
        req_headers = app.current_request.headers
        if not verify_token(req_headers, req, config["signing_secret"]):
            return "Slack signing secret not valid"

        payload = slack_payload_extractor(req)

        logger.debug(f"Slack extracted payload for interactive: {payload}")

        action = create_action(payload, config)

        action.perform_interactive()
    except Exception:
        logger.critical("Caught unhandled exception.", exc_info=True)

    return ""


@app.route(
    "/command", methods=["POST"], content_types=["application/x-www-form-urlencoded"]
)
def command():
    try:
        req = app.current_request.raw_body.decode()
        req_headers = app.current_request.headers
        if not verify_token(req_headers, req, config["signing_secret"]):
            return "Slack signing secret not valid"

        payload = slack_payload_extractor(req)

        logger.info(f"Slack extracted payload for command: {payload}")

        action = create_action(payload, config)

        action.perform_action()
    except Exception:
        logger.critical("Caught unhandled exception.", exc_info=True)

    return ""


@app.schedule("rate(1 day)")
def check_user_locks(event):
    if config["enable_lock_reminder"]:
        remind_users(
            slack=Slack(slack_token=config["bot_access_token"]),
            backend_url=config["backend_url"],
        )
