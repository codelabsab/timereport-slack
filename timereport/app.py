from chalice import Chalice
import os
import json
import logging

from chalicelib.lib.factory import factory, json_factory
from chalicelib.lib.add import post_event
from chalicelib.lib.delete import delete_event
from chalicelib.lib.slack import (slack_payload_extractor, slack_responder,
                                  slack_client_responder, submit_message_menu,
                                  delete_message_menu)

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
        response_url = payload['response_url']

        if selection == "submit_yes":
            if payload.get('callback_id') == 'delete':
                message = payload['original_message']['attachments'][0]['fields']
                user_id = payload['user']['id']
                date = message[1]['value']
                delete_by_date = delete_event(f'{backend_url}/event', user_id, date)
                if isinstance(delete_by_date, tuple):
                    app.log.debug(f'Failed to return anything: {delete_by_date[1]}')
                else:
                    for r in delete_by_date:
                        slack_responder(response_url, f'```{str(r)}```')
                logger.info('delete event posted')
                slack_responder(url=response_url, msg=f'successfully deleted entry: {date}')
                return ''

            if payload.get('callback_id') == 'add':
                events = json_factory(payload)
                for event in events:
                    post_event(f'{backend_url}/event', json.dumps(event))
                logger.info(f'python url is: {backend_url}')
                slack_responder(url=response_url, msg='Added successfully')
                return ''
        else:
            slack_responder(url=response_url, msg="Action canceled")
            return ''

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
            user_id=user_id,
            attachment=attachment
        )

        if slack_client_response.status_code != 200:
            app.log.error(
                f"""Failed to send response to slack. Status code was: {slack_client_response.status_code}.
                The response from slack was: {slack_client_response.text}"""
            )
            return "Slack response to user failed"
        else:
            app.log.debug(f"Slack client response was: {slack_client_response.text}")

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

        return ''

    if action == "delete":
        app.log.debug(f"Running delete action with: {params}")
        date = params.pop()
        attachment = delete_message_menu(payload.get('user_name')[0], date)
        app.log.debug(f"Attachment is: {attachment}. user_name is {payload.get('user_name')[0]}")

        slack_client_response = slack_client_responder(
            token=os.getenv('slack_token'),
            user_id=user_id,
            attachment=attachment
        )
        if slack_client_response.status_code != 200:
            app.log.error(
                f"""Failed to send response to slack. Status code was: {slack_client_response.status_code}.
                The response from slack was: {slack_client_response.text}"""
            )
            return "Slack response to user failed"
        else:
            app.log.debug(f"Slack client response was: {slack_client_response.text}")

        return ''

    slack_responder(response_url, "Unsupported action")
    return ''
