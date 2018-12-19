import json
import logging

from timereport.lib import factory
from timereport.lib.slack import slack_payload_extractor, verify_token, verify_actions, verify_reasons
from timereport.lib import add

logger = logging.getLogger()

with open('config.json') as fd:
    config = json.load(fd)
    valid_reasons = config['valid_reasons']
    valid_actions = config['valid_actions']
    backend_url = config['backend_url']
    logger.setLevel(config['log_level'])

def lambda_handler(event, context):

    payload: dict = slack_payload_extractor(event)

    response = factory.factory(payload)

    # needs to do something on True or False return statement
    verify_token(payload['token'])
    verify_reasons(valid_reasons, payload['reason'])
    verify_actions(valid_actions, payload['action'])

    for resp in response:
        if payload['action'] == 'add':
            add.post_to_backend(backend_url, resp.__dict__, payload['team_id'])
            exit(0)
