from chalice import Chalice
import os
import json
import logging

from chalicelib.lib.factory import factory, json_factory
from chalicelib.lib.add import post_event
from chalicelib.lib.delete import delete_event
from chalicelib.lib.slack import (slack_payload_extractor, slack_responder,
                                  slack_client_responder, submit_message_menu,
                                  delete_message_menu, verify_token)

from chalicelib.lib.helpers import parse_config
from chalicelib.action import Action

app = Chalice(app_name='timereport')
app.debug = True


logger = logging.getLogger()

dir_path = os.path.dirname(os.path.realpath(__file__))
config = parse_config(f'{dir_path}/chalicelib/config.yaml')
config['backend_url'] = os.getenv('backend_url')
config['bot_access_token'] = os.getenv('bot_access_token')
config['signing_secret'] = os.getenv('signing_secret')
logger.setLevel(config['log_level'])

@app.route('/interactive', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def interactive():
    req = app.current_request.raw_body.decode()
    payload = slack_payload_extractor(req)
    # interactive session
    selection = payload.get('actions')[0].get('value')
    logger.info(f"Selection is: {selection}")
    response_url = payload['response_url']

    if selection == "submit_yes":
        if payload.get('callback_id') == 'delete':
            message = payload['original_message']['attachments'][0]['fields']
            user_id = payload['user']['id']
            date = message[1]['value']
            delete_by_date = delete_event(f"{config['backend_url']}/event", user_id, date)
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
                post_event(f"{config['backend_url']}/event", json.dumps(event))
            logger.info(f"python url is: {config['backend_url']}")
            slack_responder(url=response_url, msg='Added successfully')
            return ''
    else:
        slack_responder(url=response_url, msg="Action canceled")
        return ''


@app.route('/command', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index():
    req = app.current_request.raw_body.decode()
    req_headers = app.current_request.headers
    req_raw_body = app.current_request.raw_body
    if not verify_token(req_headers, req_raw_body, config['signing_secret']):
        return 'Slack signing secret not valid'

    payload = slack_payload_extractor(req)

    logger.info(f'payload is: {payload}')

    action = Action(payload, config)

    action.perform_action()

    return ''
