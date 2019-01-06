from chalice import Chalice
import os
import json
import logging
import ast

from chalicelib.lib.factory import factory, date_to_string, json_serial
from chalicelib.lib.slack import slack_payload_extractor, verify_token, verify_actions, verify_reasons, slack_responder, slack_client_responder, submit_message_menu

from chalicelib.lib.add import create_event
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
    if 'body' in req:
        event = ast.literal_eval(req)
    else:
        event = dict(body=req)
    payload = slack_payload_extractor(event['body'])
    # when we respond to slack message with submit button
    # we check if type is interactive message
    for t in payload.values():
        if 'type' in t:
            payload = json.loads(t)
            if payload.get('type') == "interactive_message":
                selection = payload.get('actions')[0].get('value')

                if selection == "submit_yes":
                    # here we post to database
                    # todo

                    return '', 200
                else:
                    return 'canceling...', 200
        else:
            app.log.debug(f'no type in payload {payload}')

    params = payload['text'].split()
    response_url = payload.get('response_url')
    action = params.pop(0)
    channel_id = payload.get('channel_id')
    user_id = payload.get('user_id')

    if action == "add":
        events = factory(payload)
        user_name = events[0].get('user_name')
        reason = events[0].get('reason')
        date_start = events[0].get('event_date').isoformat().split('T')[0]
        date_end = events[-1].get('event_date').isoformat().split('T')[0]
        hours = events[0].get('hours')
        # create attachment with above values for submit button
        attachment = submit_message_menu(user_name, reason, date_start, date_end, hours)
        slack_client_response = slack_client_responder(token=config['slack_token'], channel_id=channel_id, user_id=user_id, attachment=attachment)
        if isinstance(slack_client_response, tuple):
            app.log.debug(f'Failed to return anything: {slack_client_response[1]}')
        else:
            app.log.debug(f'response from slack responder is {slack_client_response}')

            for e in slack_client_response:
                app.log.debug(f'response is {e}')
                return 200

        #for e in events:
        #    create_event(f'{python_backend_url}/event', json.dumps(e, default=json_serial))
        #slack_responder(response_url, "Add action OK????? - we need to verify")

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
