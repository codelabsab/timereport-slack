import os
from timereport.lib.helpers import parse_config


def test_parsing_config():
    test_config = parse_config()
    test_config.get('SLACK TOKEN') == 'fake token'

