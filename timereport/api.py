import logging
import os

from timereport.lib.factory import factory, date_to_string
from timereport.lib.slack import slack_payload_extractor, verify_token, verify_actions, verify_reasons
from timereport.lib.add import post_to_backend
from timereport.lib.list import get_between_date
from timereport.lib.helpers import parse_config

logger = logging.getLogger()

dir_path = os.path.dirname(os.path.realpath(__file__))
config = parse_config(f'{dir_path}/config.json')
valid_reasons = config['valid_reasons']
valid_actions = config['valid_actions']
backend_url = config['backend_url']
python_backend_url = config['python_backend_url']
logger.setLevel(config['log_level'])


def lambda_handler(event, context):

    payload = slack_payload_extractor(event)
    events = factory(payload)
    action = payload['text'].split('+')[0]
    command = payload['text'].split('+')[1:]
    auth_token = payload['team_id']

    # needs to do something on True or False return statement
    verify_token(payload['token'])
    verify_reasons(valid_reasons, command[0])
    verify_actions(valid_actions, action)

    if action == "add":
        for e in events:
            post_to_backend(backend_url, e, auth_token)

    if action == "list":

        # get/fetch from db for user_id with date_range
        # we only need first and last for listing between date range

        start_date = date_to_string(events[0]['event_date'])
        end_date = date_to_string(events.pop()['event_date'])
        get_between_date(
            backend_url,
            start_date,
            auth_token,
            end_date,
        )

