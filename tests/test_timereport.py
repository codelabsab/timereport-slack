from timereport import api
import json
from . import test_data
from mockito import when, mock, unstub
from botocore.vendored import requests
import pytest
import logging

logging.getLogger().setLevel(logging.CRITICAL)


def test_lambda_handler():
    fake_event = json.loads(test_data.d)
    response = mock({'status_code': 200, 'text': 'Ok'})
    when(requests).post(
        'https://hooks.slack.com/commands/T2FG58LDV/491076166711/bVUlrKZrnElSOBUqn01FoxNf',
        data='{"text": "add vab today"}',
        headers={'Content-Type': 'application/json'}
    ).thenReturn(response)

    assert api.lambda_handler(fake_event, context=None) == 200
    unstub()


def test_validate_add():

    fake_actions = {'add': 'foo'}
    assert api.get_action("add fake args", [*fake_actions.keys()]) == 'add'


def test_faulty_action():
    with pytest.raises(ValueError):
        assert api.get_action(text="fake_argument", valid_actions=['fake'])


def test_add_action():
    assert api.add_action(['vab', 'args']) is None


def test_add_faulty_action():
    with pytest.raises(ValueError):
        assert api.add_action(['fake', 'args'])


def test_validate_date():
    assert api.validate_date('2018-10-01') is None


def test_validate_date_invalid_month():
    with pytest.raises(ValueError):
        api.validate_date('2018-13-01')


def test_validate_date_invalid_format():
    with pytest.raises(ValueError):
        api.validate_date('2018:12:01')
