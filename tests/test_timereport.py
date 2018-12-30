import os
import datetime
from timereport.lib.helpers import parse_config
from timereport.lib.slack import slack_payload_extractor
from timereport.lib.factory import factory

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_parsing_config():
    test_config = parse_config(f'{dir_path}/config.json')
    mandatory_options = ('SLACK_TOKEN', 'db_url', 'aws_access_key_id', 'aws_secret_access_key')
    for option in mandatory_options:
        assert isinstance(option, str)
        assert test_config.get(option) is not None


def test_slack_payload_extractor():
    fake_data = slack_payload_extractor({'body': 'foo=bar&text=fake+text'})
    assert isinstance(fake_data, dict)
    assert fake_data.get('foo') == 'bar'
    assert fake_data.get('text') == 'fake text'


def test_factory():
    fake_order = dict(user_id='fake', user_name='fake mcFake', text='fake_cmd=do_fake+fake_reason+2018-01-01')
    fake_result = factory(fake_order)
    assert isinstance(fake_result, list)
    test_data = fake_result.pop()
    assert isinstance(test_data.get('event_date'), datetime.datetime)
    for item in ('user_id', 'user_name', 'reason', 'hours'):
        assert isinstance(item, str)
