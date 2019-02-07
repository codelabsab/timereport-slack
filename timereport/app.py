from chalice import Chalice
import os
import json
import logging

from chalicelib.lib.factory import factory, json_factory
from chalicelib.lib.add import post_event
from chalicelib.lib.slack import (slack_payload_extractor, slack_responder,
                                 slack_client_responder, submit_message_menu)

from chalicelib.lib.list import get_between_date, get_user_by_id
from chalicelib.lib.helpers import parse_config

app = Chalice(app_name='timereport')
app.debug = True


logger = logging.getLogger()

dir_path = os.path.dirname(os.path.realpath(__file__))
config = parse_config(f'{dir_path}/chalicelib/config.json')
valid_reasons = config['valid_reasons']
valid_actions = config['valid_actions']
python_backend_url = config['python_backend_url']
logger.setLevel(config['log_level'])


@app.route('/', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index():
    req = app.current_request.raw_body.decode()
    payload = slack_payload_extractor(req)
    # interactive session
    if payload.get('type') == "interactive_message":
        selection = payload.get('actions')[0].get('value')
        logger.info(f"Selection is: {selection}")
        if selection == "submit_yes":
            events = json_factory(payload)
            logger.info(f"{events}")
            for event in events:
                # post_event(python_backend_url, event)
                post_event(f'{python_backend_url}/event', json.dumps(event))
            logger.info(f'python url is: {python_backend_url}')
            return '', 200
        else:
            return 'canceling...', 200

    logger.info(f'payload is: {payload}')
    params = payload['text'][0].split()
    response_url = payload.get('response_url')[0]
    action = params.pop(0)
    channel_id = payload.get('channel_id')[0]
    user_id = payload.get('user_id')[0]

    if action == "add":
        events = factory(payload)
        logger.info(f"Events is: {events}")
        user_name = events[0].get('user_name')
        reason = events[0].get('reason')
        date_start = events[0].get('event_date').isoformat().split('T')[0]
        date_end = events[-1].get('event_date').isoformat().split('T')[0]
        hours = events[0].get('hours')
        # create attachment with above values for submit button
        attachment = submit_message_menu(user_name, reason, date_start, date_end, hours)

        slack_client_response = slack_client_responder(
            token=config['slack_token'],
            channel_id=channel_id,
            user_id=user_id,
            attachment=attachment
        )
        if isinstance(slack_client_response, tuple):
            app.log.debug(f'Failed to return anything: {slack_client_response[1]}')
        else:
            app.log.debug(f'response from slack responder is {slack_client_response}')

            for e in slack_client_response:
                app.log.debug(f'response is {e}')
                return 200

        return 200

    if action == "list":
        get_by_user = get_user_by_id(f'{python_backend_url}/user', payload.get('user_id'))
        if isinstance(get_by_user, tuple):
            app.log.debug(f'Failed to return anything: {get_by_user[1]}')
        else:
            for r in get_by_user:
                slack_responder(response_url, f'```{str(r)}```')

        event_date = ''.join(params[-1:])
        if ':' in event_date:
            # temporary solution

            start_date = event_date.split(':')[0]
            end_date = event_date.split(':')[1]

            get_by_date = get_between_date(f"{python_backend_url}/user/{payload.get('user_id')}", start_date, end_date)

            for r in get_by_date:
                slack_responder(response_url, f'```{str(r)}```')

        return 200
