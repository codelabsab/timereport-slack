# only use included libraries
# for aws lambda

import logging
import json
from urllib.parse import parse_qs
from botocore.vendored import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Received event is dumped in JSON format:\n{json.dumps(event, indent=2)}")

    logger.info(f"Recevied event body is parsed \n {parse_qs(event['body'])}")

    body = parse_qs(event['body'])

    # this is what we get back from a slash command as list
    # so we get the string only using index 0

    token = body['token'][0]
    team_id = body['team_id'][0]
    team_domain = body['team_domain'][0]
    channel_id = body['channel_id'][0]
    channel_name = body['channel_name'][0]
    user_id = body['user_id'][0]
    user_name = body['user_name'][0]
    command = body['command'][0]
    text = body['text'][0]
    response_url = body['response_url'][0]
    trigger_id = body['trigger_id'][0]

    response = requests.post(
        response_url, data=json.dumps(dict(text=text)),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
    else:
        return 200