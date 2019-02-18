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
config = parse_config(f'{dir_path}/chalicelib/config.yaml')
valid_reasons = config['valid_reasons']
valid_actions = config['valid_actions']
backend_url = config['backend_url']
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
                post_event(f'{backend_url}/event', json.dumps(event))
            logger.info(f'python url is: {backend_url}')
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

        '''
        Events is: [
        {
            'user_id': ['U2FG26ZFF'], 
            'user_name': ['toma'], 
            'reason': 'vab',
            'event_date': datetime.datetime(2019, 2, 7, 0, 0),
            'hours': '8'},
            {
                'user_id': ['U2FG26ZFF'],
                'user_name': ['toma'],
                'reason': 'vab', 
                'event_date': datetime.datetime(2019, 2, 8, 0, 0),
                'hours': '8'
            }
        }
        '''

        events = factory(payload)
        if not events:
            return slack_responder(response_url, 'Wrong arguments for add command')


        logger.info(f"Events is: {events}")
        logger.info(f"Token from os.environ is: {os.getenv('slack_token')}")
        user_name = events[0].get('user_name')[0]
        reason = events[0].get('reason')
        date_start = events[0].get('event_date')
        date_end = events[-1].get('event_date')
        hours = events[0].get('hours')
        # create attachment with above values for submit button
        attachment = submit_message_menu(user_name, reason, date_start, date_end, hours)
        logger.info(f"Attachment is: {attachment}")
        slack_client_response = slack_client_responder(
            token=os.getenv('slack_token'),
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

        return ''

    if action == "list":
        get_by_user = get_user_by_id(f'{backend_url}/user', user_id)
        if isinstance(get_by_user, tuple):
            app.log.debug(f'Failed to return anything: {get_by_user[1]}')
        else:
            for r in get_by_user:
                slack_responder(response_url, f'```{str(r)}```')

        event_date = ''.join(params[-1:])
        if ':' in event_date:
            # temporary solution

            start_date, end_date = event_date.split(':')

            get_by_date = get_between_date(f"{backend_url}/user/{user_id}", start_date, end_date)

            for r in get_by_date:
                slack_responder(response_url, f'```{str(r)}```')

        return 200

    slack_responder(response_url, "Unsupported action")
