import json
from datetime import datetime

import pytest
import requests
from chalicelib.action import BaseAction, create_action
from mockito import mock, unstub, when

from . import test_data

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


def test_perform_empty_action():
    fake_payload.pop("text", None)
    fake_payload["user_name"] = "fake_username"
    action = create_action(fake_payload, fake_config)
    when(action).send_response(...).thenReturn("")
    assert action.perform_action() == ""
    assert action.action == "help"
    unstub()


def test_valid_number_of_args():
    fake_action = BaseAction(fake_payload, fake_config)
    fake_action.arguments = ["fake_arg_1"]

    # Should be valid since we have provided the minimum amount
    fake_action.min_arguments = 1
    fake_action.max_arguments = 1
    assert fake_action._valid_number_of_args() is True

    fake_action.arguments.append("fake_arg_2")

    # Should be valid since we have provided the miniumum and maxiumum amount
    fake_action.min_arguments = 1
    fake_action.max_arguments = 2
    assert fake_action._valid_number_of_args() is True

    # Should be false since we don't have the minimum amount
    fake_action.min_arguments = 3
    fake_action.max_arguments = 3
    assert fake_action._valid_number_of_args() is False

    # Should be false since we don't have the maximum amount
    fake_action.min_arguments = 1
    fake_action.max_arguments = 1
    assert fake_action._valid_number_of_args() is False
