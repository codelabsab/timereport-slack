import timereport.api as api

from tests.test_data import data as event
import os

def test_factory():
    # set os.environ SLACK_TOKEN
    os.environ["SLACK_TOKEN"] = api.config['SLACK_TOKEN']
    api.lambda_handler(event, None)