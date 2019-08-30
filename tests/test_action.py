import pytest
from mockito import when, mock, unstub
import botocore.vendored.requests.api as requests
from chalicelib.action import Action
from . import test_data
import json


fake_payload = dict(
    text=["unsupported args"],
    response_url=["http://fakeurl.nowhere"],
    user_id=["fake_userid"],
)
fake_config = dict(
    bot_access_token="fake token", backend_url="http://fakebackend.nowhere"
)


def test_perform_unsupported_action():
    action = Action(fake_payload, fake_config)
    when(action).send_response(message="Unsupported action: unsupported").thenReturn("")
    assert action.perform_action() == ""
    unstub()


def test_perform_edit_action():
    fake_payload["text"] = ["edit fake argument"]
    action = Action(fake_payload, fake_config)
    when(action).send_response(message="Edit not implemented yet").thenReturn("")
    assert action.perform_action() == ""
    unstub()


def test_perform_add_action():
    fake_payload["text"] = ["add vab 2019-01-01"]
    fake_payload["user_name"] = "fake username"
    action = Action(fake_payload, fake_config)
    action.user_id = "fake_userid"
    action.date_start = "2019-01-01"
    action.date_end = "2019-01-01"
    when(action).send_response().thenReturn()
    when(requests).get(
        url=f"{fake_config['backend_url']}/event/users/{action.user_id}", 
        params={
            "startDate": action.date_start,
            "endDate": action.date_end,
        }
    ).thenReturn(mock({"status_code": 200, "text": '[{"lock": false}]'}))
    assert action.perform_action() == ""
    unstub()


def test_perform_delete_action():
    fake_payload["text"] = ["delete 2019-01-01"]
    fake_payload["user_name"] = "fake_username"
    action = Action(fake_payload, fake_config)
    when(action).send_response().thenReturn()
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
    when(action).send_response(message="```fake list output```").thenReturn("")
    when(requests).get(
        url=f"{fake_config['backend_url']}/event/users/fake_userid", params=None
    ).thenReturn(mock({"status_code": 200, "text": "fake list output"}))
    assert action.perform_action() == ""
    unstub()

def test_perform_lock_check():
    fake_payload["text"] = ["fake"]
    action = Action(fake_payload, fake_config)
    action.user_id = "fake_user"
    action.date_start = "2019-01-01"
    action.date_end = "2019-01-02"
    when(requests).get(
        url=f"{fake_config['backend_url']}/event/users/{action.user_id}", 
        params={
            "startDate": action.date_start,
            "endDate": action.date_end,
        }
    ).thenReturn(mock({"status_code": 200, "text":'[{"lock":false}]'}))
    test = action.check_lock_state()
    assert test is False
    unstub()

def test_perform_lock():
    fake_payload["text"] = ["lock 2019-01"]
    action = Action(fake_payload, fake_config)
    action.user_id = "fake_userid"
    when(action).send_response(message='Lock successful! :lock: :+1:').thenReturn()
    when(requests).post(
        url=f"{fake_config['backend_url']}/lock",
        data=json.dumps({'user_id': 'fake_userid', 'event_date': '2019-01'}),
        headers={'Content-Type': 'application/json'},
    ).thenReturn(mock({"status_code": 200}))
    assert action.perform_action() == ""
    unstub()