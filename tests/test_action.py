import pytest
from mockito import when, mock, unstub
import requests
from chalicelib.action import Action
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
    action = Action(fake_payload, fake_config)
    when(action).send_response(message="Unsupported action: unsupported").thenReturn("")
    assert action.perform_action() == ""
    unstub()


def test_perform_empty_edit_action():
    fake_payload["text"] = ["edit 2019-01-01"]
    action = Action(fake_payload, fake_config)
    when(action).send_response(
        message="No event for date 2019-01-01 to edit. :shrug:"
    ).thenReturn()
    when(action)._get_events(date_str="2019-01-01").thenReturn("[]")
    assert action.perform_action() == ""
    unstub()


def test_perform_add_action():
    fake_payload["text"] = ["add vab 2019-01-01"]
    fake_payload["user_name"] = "fake username"
    action = Action(fake_payload, fake_config)
    action.user_id = "fake_userid"
    action.date_start = "2019-01-01"
    action.date_end = "2019-01-01"
    when(action).send_response(message="").thenReturn()
    when(requests).get(
        url=f"{fake_config['backend_url']}/event/users/{action.user_id}",
        params={"startDate": action.date_start, "endDate": action.date_end},
    ).thenReturn(mock({"status_code": 200, "text": '[{"lock": false}]'}))
    assert action.perform_action() == ""
    unstub()


def test_perform_help_action():
    fake_payload["text"] = ["help"]
    fake_payload["user_name"] = "fake_username"
    action = Action(fake_payload, fake_config)
    when(action).send_response(message=action.perform_action.__doc__).thenReturn("")
    assert action.perform_action() == ""
    unstub()


def test_perform_empty_action():
    fake_payload.pop("text", None)
    fake_payload["user_name"] = "fake_username"
    action = Action(fake_payload, fake_config)
    when(action).send_response(message=action.perform_action.__doc__).thenReturn("")
    assert action.perform_action() == ""
    assert action.action == "help"
    unstub()


def test_perform_list_action():
    fake_payload["text"] = ["list"]
    fake_payload["user_name"] = "fake_username"
    action = Action(fake_payload, fake_config)

    when(action).send_block(message="fake list output").thenReturn("")
    when(requests).get(
        url=f"{fake_config['backend_url']}/event/users/fake_userid",
        params={
            "startDate": datetime.now().strftime("%Y-%m-01"),
            "endDate": datetime.now().strftime("%Y-%m-31"),
        },
    ).thenReturn(mock({"status_code": 200, "text": "fake list output"}))
    assert action.perform_action() == ""
    unstub()


def test_perform_lock():
    fake_payload["text"] = ["lock 2019-01"]
    action = Action(fake_payload, fake_config)
    action.user_id = "fake_userid"
    when(action).send_response(message="Lock successful! :lock: :+1:").thenReturn()
    when(requests).post(
        url=f"{fake_config['backend_url']}/lock",
        data=json.dumps({"user_id": "fake_userid", "event_date": "2019-01"}),
        headers={"Content-Type": "application/json"},
    ).thenReturn(mock({"status_code": 200}))
    assert action.perform_action() == ""
    unstub()
