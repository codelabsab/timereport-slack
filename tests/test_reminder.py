import json

import pytest
import requests
from mockito import expect, kwargs, mock, unstub, verify, when

from chalicelib.lib.reminder import last_month, remind_users
from chalicelib.lib.slack import Slack

fake_config = dict(backend_url="http://localhost:8010", bot_access_token="secret_token")


def test_remind_user_without_lock():
    when(requests).get(url=f"{fake_config['backend_url']}/users", **kwargs).thenReturn(
        mock({"status_code": 200, "text": json.dumps(dict(testuser="test"))})
    )

    when(requests).get(
        url=f"{fake_config['backend_url']}/users/testuser/locks",
        **kwargs,
    ).thenReturn(mock({"status_code": 200, "text": json.dumps([])}))

    when(requests).post(
        url="https://slack.com/api/chat.postMessage", **kwargs
    ).thenReturn(mock({"status_code": 200}))

    remind_users(Slack(fake_config["bot_access_token"]), fake_config["backend_url"])

    verify(requests, times=1).post(
        url="https://slack.com/api/chat.postMessage", **kwargs
    )

    unstub()


def test_remind_user_with_lock():
    when(requests).get(url=f"{fake_config['backend_url']}/users", **kwargs).thenReturn(
        mock({"status_code": 200, "text": json.dumps(dict(testuser="test"))})
    )

    lock_evt = dict(event_date=last_month(), user_id="testuser")
    when(requests).get(
        url=f"{fake_config['backend_url']}/users/testuser/locks",
        **kwargs,
    ).thenReturn(mock({"status_code": 200, "text": json.dumps([lock_evt])}))

    with expect(requests, times=0).post(...):
        remind_users(Slack(fake_config["bot_access_token"]), fake_config["backend_url"])

    unstub()
