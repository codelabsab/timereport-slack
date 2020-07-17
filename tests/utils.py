import hashlib
import hmac
import json
from typing import Dict, List
from unittest import mock
from urllib.parse import urlencode

from tests.conftest import signing_secret


def respond_interactively(
    *, chalice_app, attachments, user_id, user_name, action="submit_yes"
):
    """
    Mocks slacks menu driven responses, for example used to verify adding entries.

    :param chalice_app: mocked chalice app (from fixture with same name)
    :param attachments: attachments from call_from_slack, what we're responding to
    :param user_id: id of the user
    :param user_name: name of the user
    :param action: response from user
    :return: Dict with `slack_message` containing the message to slack and `response` containing the http response
    """
    payload = dict(
        response_url="example.com",
        user_id=[user_id],
        user_name=[user_name],
        actions=[dict(value=action)],
        callback_id="add",
        user=dict(id=user_id),
        original_message=dict(attachments=attachments),
    )

    return _perform_call(chalice_app, "/interactive", payload)


def call_from_slack(
    *, chalice_app, full_command: str, user_id: str, user_name: str,
) -> Dict[str, str]:
    """
    Mock command sent from slack.

    :param chalice_app: mocked chalice app (from fixture with same name)
    :param full_command: the command string, as written by a user after `/timereport `
    :param user_id: id of the user
    :param user_name: name of the user
    :return: Dict with `slack_message` containing the message to slack and `response` containing the http response
    """
    command = full_command.split(" ")[0]
    payload = dict(
        command=command,
        text=[full_command],
        response_url="example.com",
        user_id=[user_id],
        user_name=[user_name],
    )

    return _perform_call(chalice_app, "/command", payload)


def _perform_call(chalice_app, endpoint, payload):
    timestamp = 1531420618
    body = urlencode(dict(payload=json.dumps(payload)))
    request_basestring = f"v0:{timestamp}:{body}"
    new_sign = f'v0={hmac.new(bytes(signing_secret, "utf-8"), bytes(request_basestring, "utf-8"), hashlib.sha256).hexdigest()}'

    with mock.patch("chalicelib.lib.slack.requests") as mock_request:
        mock_request.post.return_value = mock.Mock(status_code=200)
        response = chalice_app.handle_request(
            method="POST",
            path=endpoint,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Slack-request-timestamp": str(timestamp),
                "X-Slack-Signature": new_sign,
            },
            body=body,
        )

    return dict(slack_message=mock_request.post.call_args, response=response)


def get_raw_block_text(*, slack_message):
    """
    Parse a slack message returning the raw text from "blocks"

    :param slack_message: Slack message as returned from call_from_slack
    :return: String with the raw text (without formatting)
    """
    blocks = slack_message[1]["json"]["blocks"]
    # Flatten nested dict:
    # blocks = [{"text": {"text": "Some text"}}]
    return "".join([b.get("text", {}).get("text", "") for b in blocks])
