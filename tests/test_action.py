import pytest
from mockito import when, mock, unstub
import botocore.vendored.requests.api as requests
from chalicelib.action import Action


fake_payload = dict(
    text=["fake action", "test"],
    response_url=["http://fakeurl.nowhere"],
    user_id=["fake user"],
)
fake_config = dict(slack_token="fake token")


def test_perform_unsupported_action():
    action = Action(fake_payload, fake_config)
    when(requests).post(
        url=action.response_url,
        json={"text": "Unsupported action: fake"},
        headers={"Content-Type": "application/json"},
    ).thenReturn(mock({"status_code": 200}))
    assert action.perform_action() == ""
    unstub()


def test_perform_edit_action():
    fake_payload["text"] = ["edit", "fake argument"]
    action = Action(fake_payload, fake_config)
    when(requests).post(
        url=action.response_url,
        json={"text": "Edit not implemented yet"},
        headers={"Content-Type": "application/json"},
    ).thenReturn(mock({"status_code": 200}))
    assert action.perform_action() == ""
    unstub()
