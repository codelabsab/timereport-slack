import os
import datetime
from timereport.chalicelib.lib.helpers import parse_config, verify_actions, verify_reasons
from timereport.chalicelib.lib.slack import slack_payload_extractor, verify_token
from timereport.chalicelib.lib.factory import factory
from timereport.chalicelib.lib.add import create_event
from mockito import when, mock, unstub
import botocore.vendored.requests.api as requests

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_parsing_config():
    test_config = parse_config(f'{dir_path}/config.json')
    mandatory_options = ('SLACK_TOKEN', 'db_url', 'aws_access_key_id', 'aws_secret_access_key')
    for option in mandatory_options:
        assert isinstance(option, str)
        assert test_config.get(option) is not None


def test_slack_payload_extractor():
    fake_data = slack_payload_extractor('foo=bar&text=fake+text')
    assert isinstance(fake_data, dict)
    assert fake_data.get('foo') == 'bar'
    assert fake_data.get('text') == 'fake text'


def test_factory():
    fake_order = dict(user_id='fake', user_name='fake mcFake', text='fake_cmd=do_fake fake_reason 2018-01-01')
    fake_result = factory(fake_order)
    assert isinstance(fake_result, list)
    test_data = fake_result.pop()
    assert isinstance(test_data.get('event_date'), datetime.datetime)
    for item in ('user_id', 'user_name', 'reason', 'hours'):
        assert isinstance(test_data[item], str)


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

    assert create_event(fake_url, fake_data) is True
    unstub()


def test_create_event_failure():
    fake_url = 'http://fake.com'
    fake_data = 'fake data'
    when(requests).post(
        url=fake_url, json=fake_data, headers={'Content-Type': 'application/json'}
    ).thenReturn(mock({'status_code': 500}))
    assert create_event(fake_url, fake_data) is False
    unstub()
