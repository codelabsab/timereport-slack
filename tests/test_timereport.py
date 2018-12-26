import os
import tests.test_data
import datetime
from timereport.lib.helpers import parse_config
from timereport.lib.slack import slack_payload_extractor
from timereport.lib.factory import factory

dir_path = os.path.dirname(os.path.realpath(__file__))
test_config = parse_config(f'{dir_path}/config.json')

def test_parsing_config():

    assert test_config.get('SLACK_TOKEN') == 'fake token'
    assert test_config.get('db_url') == 'http://127.0.0.1:8000'
    assert test_config.get('aws_access_key_id') == 'my_access_key_id'
    assert test_config.get('aws_secret_access_key') == 'my_secret_access_key'


def test_slack_payload_extractor():
    assert isinstance(slack_payload_extractor({'body': 'fake=fake'}), dict)


def test_factory():
    fake_order = dict(user_id='fake', user_name='fake mcFake', text='fake_cmd=do_fake+fake_reason+2018-01-01')
    fake_result = factory(fake_order)
    assert isinstance(fake_result, list)
    test_data = fake_result.pop()
    assert isinstance(test_data.get('event_date'), datetime.datetime)
    for item in ('user_id', 'user_name', 'reason', 'hours'):
        assert isinstance(item, str)
