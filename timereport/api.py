import json
import logging

from timereport.lib import factory
from timereport.lib.slack import slack_payload_extractor, verify_token

logger = logging.getLogger()

with open('config.json') as fd:
    config = json.load(fd)
    valid_reasons = config['valid_reasons']
    valid_actions = config['valid_actions']
    logger.setLevel(config['log_level'])

def lambda_handler(event, context):

    payload: dict = slack_payload_extractor(event)

    verify_token(payload['token'])
    response = factory.factory(payload)

    for resp in response:
        print(resp)




