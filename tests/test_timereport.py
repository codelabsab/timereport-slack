import os
from timereport.lib.helpers import parse_config
dir_path = os.path.dirname(os.path.realpath(__file__))


def test_parsing_config():
    test_config = parse_config(f'{dir_path}/config.json')
    assert test_config.get('SLACK_TOKEN') == 'fake token'

