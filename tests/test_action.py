import pytest
from mockito import when, mock, unstub
import requests
from chalicelib.action import create_action
from datetime import datetime
from . import test_data
import json


fake_payload = dict(
    text=["unsupported args"],
    response_url=["http://fakeurl.nowhere"],
    user_id=["fake_userid"],
    user_name=["fake_username"],
)
fake_config = dict(
    bot_access_token="fake token",
    backend_url="http://fakebackend.nowhere",
    valid_reasons=["vab"],
    format_str="%Y-%m-%d",
)


def test_perform_unsupported_action():
    action = create_action(fake_payload, fake_config)
    when(action).send_response(message="Unsupported action: unsupported").thenReturn("")
    assert action.perform_action() == ""
    unstub()


def test_perform_help_action():
    fake_payload["text"] = ["help"]
    fake_payload["user_name"] = "fake_username"
    action = create_action(fake_payload, fake_config)
    when(action).send_response(...).thenReturn("")
    assert action.perform_action() == ""
    unstub()


def test_perform_empty_action():
    fake_payload.pop("text", None)
    fake_payload["user_name"] = "fake_username"
    action = create_action(fake_payload, fake_config)
    when(action).send_response(...).thenReturn("")
    assert action.perform_action() == ""
    assert action.action == "help"
    unstub()


def test_perform_lock():
    fake_payload["text"] = ["lock 2019-01"]
    action = create_action(fake_payload, fake_config)
    action.user_id = "fake_userid"
    when(action).send_response(message="Lock successful! :lock: :+1:").thenReturn()
    when(requests).post(
        url=f"{fake_config['backend_url']}/lock",
        data=json.dumps({"user_id": "fake_userid", "event_date": "2019-01"}),
        headers={"Content-Type": "application/json"},
    ).thenReturn(mock({"status_code": 200}))
    assert action.perform_action() == ""
    unstub()


def test_valid_number_of_args():
    fake_action = create_action(fake_payload, fake_config)
    fake_action.arguments = ["fake_arg_1"]

    # Should be valid since we have provided the minimum amount
    assert fake_action._valid_number_of_args(min_args=1, max_args=1) is True

    fake_action.arguments.append("fake_arg_2")

    # Should be valid since we have provided the miniumum and maxiumum amount
    assert fake_action._valid_number_of_args(min_args=1, max_args=2) is True

    # Should be false since we don't have the minimum amount
    assert fake_action._valid_number_of_args(min_args=3, max_args=3) is False

    # Should be false since we don't have the maximum amount
    assert fake_action._valid_number_of_args(min_args=1, max_args=1) is False
