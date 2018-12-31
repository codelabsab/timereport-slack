from chalice import Chalice
import os
import json
import logging

from chalicelib.lib.factory import factory, date_to_string, json_serial
from chalicelib.lib.slack import slack_payload_extractor, verify_token, verify_actions, verify_reasons
from chalicelib.lib.add import post_to_backend, create_event
from chalicelib.lib.list import get_between_date, get_user_by_id
from chalicelib.lib.helpers import parse_config

app = Chalice(app_name='timereport')
app.debug = True


logger = logging.getLogger()

dir_path = os.path.dirname(os.path.realpath(__file__))
config = parse_config(f'{dir_path}/config.json')
valid_reasons = config['valid_reasons']
valid_actions = config['valid_actions']
backend_url = config['backend_url']
python_backend_url = config['python_backend_url']
logger.setLevel(config['log_level'])


@app.route('/', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index():
    req = app.current_request.raw_body.decode()
    event = json.loads(req)
    payload = slack_payload_extractor(event)
    events = factory(payload)
    params = payload['text'].split()
    action = params.pop(0)
    command = params.pop(0)
    auth_token = payload['team_id']

    # needs to do something on True or False return statement
    verify_token(payload['token'])
    verify_reasons(valid_reasons, command[0])
    verify_actions(valid_actions, action)

    if action == "add":
        for e in events:
            # python-backend
            create_event(python_backend_url + '/' + 'event', json.dumps(e, default=json_serial))
            # node-backend (change $backend_url in config.json first)
            post_to_backend(backend_url, e, auth_token)

    if action == "list":

        # get/fetch from db for user_id with date_range
        # we only need first and last for listing between date range

        start_date = date_to_string(events[0]['event_date'])
        end_date = date_to_string(events[-1]['event_date'])
        # node-backend (change $backend_url in config.json first)
        get_between_date(
            backend_url,
            start_date,
            auth_token,
            end_date,
        )

        # python-backend
        get_user_by_id(python_backend_url + '/' + 'user', payload.get('user_id'))