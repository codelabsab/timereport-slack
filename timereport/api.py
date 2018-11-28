# only use included libraries
# for aws lambda

import logging
import json
from urllib.parse import parse_qs
from botocore.vendored import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

valid_actions = ('add', 'list')


def lambda_handler(event, context):
    logger.info(f"Received event is dumped in JSON format:\n{json.dumps(event, indent=2)}")

    logger.info(f"Received event body is parsed \n {parse_qs(event['body'])}")

    body = parse_qs(event['body'])
    text = body['text'][0]
    logger.info(f"Text is: {text}")

    response_url = body['response_url'][0]

    response = requests.post(
        response_url, data=json.dumps(dict(text=text)),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError( f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}")
    else:
        return 200


def validate_input(text):
    """
    Validate the commands parsed from Slack
    :param text: A string of commands
    """

    commands = text.split()
    if commands[0] not in valid_actions:
        raise ValueError("Action '{commands[0]}' is not a valid action")
