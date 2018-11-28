from timereport import api
import json
from . import test_data
from mockito import when, mock, unstub
from botocore.vendored import requests
import pytest


def test_lambda_handler():
    fake_event = json.loads(test_data.d)
    response = mock({'status_code': 200, 'text': 'Ok'})
    when(requests).post(
        'https://hooks.slack.com/commands/T2FG58LDV/491076166711/bVUlrKZrnElSOBUqn01FoxNf',
        data='{"text": "vab today"}',
        headers={'Content-Type': 'application/json'}
    ).thenReturn(response)

    assert api.lambda_handler(fake_event, context=None) == 200
    unstub()


def test_validate():
    assert api.validate_input("add fake args") is None


def test_faulty_action():
    with pytest.raises(ValueError):
        assert api.validate_input("fake_argument")
