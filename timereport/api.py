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
    text = body['text'][0]
    response_url = body['response_url'][0]

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
