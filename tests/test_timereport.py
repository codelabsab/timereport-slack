import os
import pytest
from timereport.chalicelib.lib.helpers import parse_config, verify_actions, verify_reasons
from timereport.chalicelib.lib.slack import (slack_payload_extractor, verify_token,
                                             slack_client_responder, slack_responder)
from timereport.chalicelib.lib.factory import factory, json_factory, date_to_string
from timereport.chalicelib.lib.add import post_event
from mockito import when, mock, unstub
import botocore.vendored.requests.api as requests
from datetime import datetime


dir_path = os.path.dirname(os.path.realpath(__file__))


def test_parsing_config():
    test_config = parse_config(f'{dir_path}/config.yaml')
    mandatory_options = ('log_level', 'backend_url')
    for option in mandatory_options:
        assert isinstance(option, str)
        assert test_config.get(option) is not None


def test_slack_payload_extractor_message():
    fake_data = slack_payload_extractor('command=bar&text=fake+text')
    assert isinstance(fake_data, dict)
    assert fake_data.get('command') == ['bar']
    assert fake_data.get('text') == ['fake text']


@pytest.mark.parametrize(
    "date_string",
    ["2018-01-01", "today", "today 8", "today 24", "2019-01-01:2019-02-01"]
)
def test_factory(date_string):
    fake_order = dict(
        user_id='fake',
        user_name='fake mcFake',
        text=[f'fake_cmd=do_fake fake_reason {date_string}']
    )

    fake_result = factory(fake_order)
    assert isinstance(fake_result, list)
    test_data = fake_result.pop()
    assert isinstance(test_data.get('event_date'), str)
    for item in ('user_id', 'user_name', 'reason'):
        assert isinstance(test_data[item], str)

    assert int(test_data['hours']) <= 8


def test_wrong_hours_data_type():
    fake_order = dict(
        user_id='fake',
        user_name='fake mcFake',
        text=[f'fake_cmd=do_fake fake_reason today wrong_hours']
    )
    assert factory(fake_order) is False


@pytest.mark.parametrize(
    "args_list",
    [["one", "two", "three", "four", "five"], ["one_argument"]],
)
def test_wrong_number_of_args_for_add(args_list):
    fake_order = dict(
        user_id='fake',
        user_name='fake mcFake',
        text=args_list
    )
    assert factory(fake_order) is False


def test_slack_token():
    assert verify_token('faulty fake token') is not True
    fake_test_token = 'my_fake_token'
    os.environ['slack_token'] = fake_test_token
    assert verify_token(fake_test_token) is True


def test_verify_reason():
    assert verify_reasons(['not real reasons'], 'fake') is False
    assert verify_reasons(['my fake reason'], 'my fake reason') is True


def test_verify_action():
    assert verify_actions(['not a real action'], 'fake action') is False
    assert verify_actions(['my fake action'], 'my fake action') is True


def test_create_event():
    fake_url = 'http://fake.com'
    fake_data = 'fake data'
    when(requests).post(
        url=fake_url, json=fake_data, headers={'Content-Type': 'application/json'}
    ).thenReturn(mock({'status_code': 200}))

    assert post_event(fake_url, fake_data) is True
    unstub()


def test_create_event_failure():
    fake_url = 'http://fake.com'
    fake_data = 'fake data'
    when(requests).post(
        url=fake_url, json=fake_data, headers={'Content-Type': 'application/json'}
    ).thenReturn(mock({'status_code': 500}))
    assert post_event(fake_url, fake_data) is False
    unstub()


def test_json_factory():
    from .test_data import interactive_message

    fake_result = json_factory(interactive_message)
    assert isinstance(fake_result, list)
    for item in ('user_id', 'user_name', 'reason', 'event_date', 'hours'):
        assert item in fake_result[0]


def test_date_to_string():
    test_data = date_to_string(datetime.now())
    assert isinstance(test_data, str)


def test_slack_client_responder():
    fake_url = 'http://fake.com'
    fake_data = {'channel': 'fake', 'text': 'fake from slack.py', 'attachments': 'fake'}
    fake_headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer fake'}
    when(requests).post(
        url=fake_url, json=fake_data, headers=fake_headers
    ).thenReturn(mock({'status_code': 200}))

    test_result = slack_client_responder(
        token='fake',
        channel_id='fake',
        user_id='fake',
        attachment='fake',
        url=fake_url,
    )

    assert test_result.status_code == 200
    unstub()


def test_slack_client_responder_failure():
    fake_url = 'http://fake2.com'
    fake_data = {'channel': 'fake', 'text': 'fake from slack.py', 'attachments': 'fake'}
    fake_headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer fake'}
    when(requests).post(
        url=fake_url, json=fake_data, headers=fake_headers
    ).thenReturn(mock({'status_code': 500}))

    test_result = slack_client_responder(
        token='fake',
        channel_id='fake',
        user_id='fake',
        attachment='fake',
        url=fake_url,
    )
    assert test_result.status_code != 200
    unstub()


def test_slack_responder():
    when(requests).post(
        url='fake', json={'text': 'fake message'}, headers={'Content-Type': 'application/json'}
    ).thenReturn(mock({'status_code': 200}))
    assert slack_responder(url='fake', msg='fake message') == 200
