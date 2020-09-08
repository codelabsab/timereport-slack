import json
import boto3
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
from chalicelib.lib.sqs import send_message

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
config["command_queue"] = f"timereport-slack-command-{os.getenv('environment')}"
config["enable_queue"] = os.getenv("enable_queue", False)

logger.setLevel(config["log_level"])


def dummy():
    """
    The sole purpose is to force Chalice to generate the right permissions in the policy.
    Does nothing and returns nothing.
    """
    sqs = boto3.client("sqs")
    sqs.send_message()
    sqs.get_queue_url()


@app.route(
    "/interactive",
    methods=["POST"],
    content_types=["application/x-www-form-urlencoded"],
)
def interactive():
    if False:
        dummy()

    def _handle_message(payload):
        action = create_action(payload, config)
        action.perform_interactive()

    return handle_slack_request(_handle_message)


@app.route(
    "/command", methods=["POST"], content_types=["application/x-www-form-urlencoded"]
)
def command():
    def _handle_message(payload):
        send_message(
            config["enable_queue"], config["command_queue"], payload, command_handler
        )

    return handle_slack_request(_handle_message)


def handle_slack_request(action):
    payload = None
    try:
        req = app.current_request.raw_body.decode()
        req_headers = app.current_request.headers
        if not verify_token(req_headers, req, config["signing_secret"]):
            return "Slack signing secret not valid"

        payload = slack_payload_extractor(req)

        logger.info(f"Slack extracted payload for command: {payload}")

        action(payload)
    except Exception:
        logger.critical("Caught unhandled exception.", exc_info=True)

        if isinstance(payload, dict) and "response_url" in payload:
            slack_responder(
                payload["response_url"], "Failed to handle request, try again!"
            )

    return ""


@app.on_sqs_message(queue=config["command_queue"])
def command_handler(event):
    for record in event:
        action = create_action(json.loads(record.body), config)
        action.perform_action()


@app.schedule("rate(1 day)")
def check_user_locks(event):
    if config["enable_lock_reminder"]:
        remind_users(
            slack=Slack(slack_token=config["bot_access_token"]),
            backend_url=config["backend_url"],
        )
