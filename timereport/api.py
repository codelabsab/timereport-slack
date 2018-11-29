# only use included libraries
# for aws lambda

import logging
import json
from urllib.parse import parse_qs
from botocore.vendored import requests
from . import config
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.debug(f"Received event is dumped in JSON format:\n{json.dumps(event, indent=2)}")

    logger.debug(f"Received event body is parsed \n {parse_qs(event['body'])}")

    body = parse_qs(event['body'])
    text = body['text'][0]
    logger.debug(f"Text is: {text}")

    actions = {
        'add': add_action,
        'list': list_action,
    }

    command_list = text.split()
    action = get_action(command_list.pop(0), [*actions.keys()])
    actions[action](command_list)

    response_url = body['response_url'][0]

    response = requests.post(
        response_url, data=json.dumps(dict(text=text)),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}"
        )
    else:
        return 200


def get_action(text, valid_actions):
    """
    Get the action command parsed from Slack
    :param text: A string of commands
    :param valid_actions: A list of valid actions
    :return str
    """

    action = text.split()[0]
    logger.debug(f"Action is: {action}")
    if action not in valid_actions:
        raise ValueError(f"Action '{action}' is not a valid action")

    return action


def add_action(command_list):
    add_type = command_list.pop(0)
    if add_type not in config.valid_types:
        raise ValueError(f"Value '{add_type}' is not a valid type for add")


def list_action():
    pass


def validate_date(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")