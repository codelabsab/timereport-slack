import pytest
from mockito import when, mock, unstub
import botocore.vendored.requests.api as requests
from chalicelib.action import Action
from . import test_data


fake_payload = dict(
    text=["unsupported args"],
    response_url=["http://fakeurl.nowhere"],
    user_id=["fake user"],
)
fake_config = dict(slack_token="fake token")


def test_perform_unsupported_action():
    action = Action(fake_payload, fake_config)
    when(action).send_response(message='Unsupported action: unsupported').thenReturn("")
    assert action.perform_action() == ""
    unstub()


def test_perform_edit_action():
    fake_payload["text"] = ["edit fake argument"]
    action = Action(fake_payload, fake_config)
    when(action).send_response(message='Edit not implemented yet').thenReturn("")
    assert action.perform_action() == ""
    unstub()


def test_perform_add_action():
    fake_payload["text"] = ["add vab 2019-01-01"]
    fake_payload["user_name"] = "fake username"
    action = Action(fake_payload, fake_config)
    when(action).send_response().thenReturn()
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
    fake_payload.pop('text', None)
    fake_payload["user_name"] = "fake_username"
    action = Action(fake_payload, fake_config)
    when(action).send_response(message=action.perform_action.__doc__).thenReturn("")
    assert action.perform_action() == ""
    assert action.action == "help"
    unstub()