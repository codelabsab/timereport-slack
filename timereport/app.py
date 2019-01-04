from chalice import Chalice
import os
import json
import logging
import ast

from chalicelib.lib.factory import factory, date_to_string, json_serial
from chalicelib.lib.slack import slack_payload_extractor, verify_token, verify_actions, verify_reasons, slack_responder

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
backend_url = config['backend_url']
python_backend_url = config['python_backend_url']
logger.setLevel(config['log_level'])


@app.route('/', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index():
    req = app.current_request.raw_body.decode()
    if 'body' in req:
        event = ast.literal_eval(req)
    else:
        event = dict(body=req)
    payload = slack_payload_extractor(event)
    params = payload['text'].split()
    response_url = payload.get('response_url')
    action = params.pop(0)

    # needs to do something on True or False return statement
    verify_token(payload['token'])
    #verify_reasons(valid_reasons, command[0])
    #verify_actions(valid_actions, action)

    if action == "add":
        # list of dicts [{'user_id': 'ABCDE123', 'user_name': 'test.user'}, {'user_id': 'ABCDE456' }]
        events = factory(payload)
        # verify if we want to submit to slack or not
        # post_to_slack ?
        attachment = [
            {
                "fields": [
                    {
                        "title": "User",
                        "value": f"{events[0].get('user_name')}"
                    },

                    {
                        "title": "Type",
                        "value": f"{events[0].get('reason')}"
                    },
                    {
                        "title": "Date start",
                        "value": f"{events[0].get('event_date').isoformat().split('T')[0]}"
                    },
                    {
                        "title": "Date end",
                        "value": f"{events[-1].get('event_date').isoformat().split('T')[0]}"
                    },

                    {
                        "title": "Hours",
                        "value": f"{events[0].get('hours')}"
                    }
                ],
                "footer": "Code Labs timereport",
                "footer_icon": "https://codelabs.se/favicon.ico",
                "fallback": "Submit these values?",
                "title": "Submit these values?",
                "callback_id": "submit",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "submit",
                        "text": "submit",
                        "type": "button",
                        "style": "primary",
                        "value": "submit_yes"
                    },
                    {
                        "name": "no",
                        "text": "No",
                        "type": "button",
                        "style": "danger",
                        "value": "submit_no"
                    }
                ]
            }
        ]

        app.log.debug(f'attachment is: {attachment}')
        slack_responder(response_url, attachment)
        for e in events:
            # python-backend
            create_event(f'{python_backend_url}/event', json.dumps(e, default=json_serial))
        # post back to slack
        slack_responder(response_url, "Add action OK????? - we need to verify")

    if action == "list":
        # python-backend

        # get everything
        get_by_user = get_user_by_id(f'{python_backend_url}/user', payload.get('user_id'))
        if isinstance(get_by_user, tuple):
            app.log.debug(f'Failed to return anything: {get_by_user[1]}')
        else:
            for r in get_by_user:
                slack_responder(response_url, f'```{str(r)}```')

        # get by date
        event_date = ''.join(params[-1:])
        if ':' in event_date:
            # we have provided two dates
            # maybe we should validate dates as well as we do in factory?
            # temporary solution

            start_date = event_date.split(':')[0]
            end_date = event_date.split(':')[1]

            get_by_date = get_between_date(f"{python_backend_url}/user/{payload.get('user_id')}", start_date, end_date)

            for r in get_by_date:
                slack_responder(response_url, f'```{str(r)}```')

        return 200
