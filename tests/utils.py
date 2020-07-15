import hashlib
import hmac
import json
from typing import Dict, List
from unittest import mock
from urllib.parse import urlencode

from tests.conftest import signing_secret


def call_from_slack(
    chalice_app, command: List[str], user_id: str, user_name: str
) -> Dict[str, str]:
    timestamp = 1531420618
    pl = json.dumps(
        dict(
            command=command[0],
            text=command,
            response_url="example.com",
            user_id=[user_id],
            user_name=[user_name],
        )
    )
    body = urlencode(dict(payload=pl))
    request_basestring = f"v0:{timestamp}:{body}"
    new_sign = f'v0={hmac.new(bytes(signing_secret, "utf-8"), bytes(request_basestring, "utf-8"), hashlib.sha256).hexdigest()}'

    with mock.patch("chalicelib.action.Action.send_response") as m:
        response = chalice_app.handle_request(
            method="POST",
            path="/command",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Slack-request-timestamp": str(timestamp),
                "X-Slack-Signature": new_sign,
            },
            body=body,
        )

    return dict(slack_message=m.call_args[1]["message"], response=response)
