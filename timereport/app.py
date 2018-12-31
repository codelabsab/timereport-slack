from chalice import Chalice
import os
import json
import logging

from chalicelib.lib.factory import factory, date_to_string, json_serial
from chalicelib.lib.slack import slack_payload_extractor, verify_token, verify_actions, verify_reasons, slack_responder
from chalicelib.lib.add import post_to_backend, create_event
from chalicelib.lib.list import get_between_date, get_user_by_id
from chalicelib.lib.helpers import parse_config

app = Chalice(app_name='timereport')
app.debug = True


logger = logging.getLogger()

dir_path = os.path.dirname(os.path.realpath(__file__))
config = parse_config(f'{dir_path}/chalicelib/config.json')
valid_reasons = config['valid_reasons']
valid_actions = config['valid_actions']
backend_url = config['backend_url']
python_backend_url = config['python_backend_url']
logger.setLevel(config['log_level'])


@app.route('/', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index():
    req = app.current_request.raw_body.decode()
    event = dict(body=req)
    payload = slack_payload_extractor(event)
    events = factory(payload)
    response_url = payload.get('response_url')
    params = payload['text'].split()
    action = params.pop(0)
    command = params.pop(0)
    auth_token = payload['team_id']

    # needs to do something on True or False return statement
    verify_token(payload['token'])
    #verify_reasons(valid_reasons, command[0])
    #verify_actions(valid_actions, action)

    if action == "add":
        for e in events:
            # python-backend
            create_event(python_backend_url + '/event', json.dumps(e, default=json_serial))
        # post back to slack
        slack_responder(response_url, "Add action OK")

    if action == "list":

        # get/fetch from db for user_id with date_range
        # we only need first and last for listing between date range

        start_date = date_to_string(events[0]['event_date'])
        end_date = date_to_string(events[-1]['event_date'])

        # python-backend
        response = get_user_by_id(python_backend_url + '/' + 'user', payload.get('user_id'))
        # post back to slack as a code formatted output ``` data ```
        for r in response:
            slack_responder(response_url, f'```{str(r)}```')
        return 200
