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
        user_id = payload['user']['id']
        if payload.get('callback_id') == 'delete':
            message = payload['original_message']['attachments'][0]['fields']
            date = message[1]['value']
            delete_by_date = delete_event(f"{config['backend_url']}/event/users/{user_id}", date)
            logger.info(f"Delete event posted to URL: {config['backend_url']}/event/users/{user_id}")
            if delete_by_date.status_code != 200:
                logger.debug(
                    f"Error from backend: status code: {delete_by_date.status_code}. Response text: {delete_by_date.text}"
                )
                slack_responder(url=response_url, msg=f'Got unexpected response from backend')
            else:
                slack_responder(url=response_url, msg=f'successfully deleted entry: {date}')
            return ''

        if payload.get('callback_id') == 'add':
            msg = 'Added successfully'
            events = json_factory(payload)
            failed_events = list()
            for event in events:
                response = post_event(f"{config['backend_url']}/event/users/{user_id}", json.dumps(event))
                if response.status_code != 200:
                    logger.debug(
                        f"Event {event} got unexpected response from backend: {response.text}"
                    )
                    failed_events.append(event.get('event_date'))

            if failed_events:
                logger.debug(f"Got {len(failed_events)} events")
                msg = (
                    f"Successfully added {len(events) - len(failed_events)} events.\n"
                    "These however failed: ```{failed_events} ```"
                )
            slack_responder(url=response_url, msg=msg)
            return ''
    else:
        slack_responder(url=response_url, msg="Action canceled")
        return ''


@app.route('/command', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index():
    req = app.current_request.raw_body.decode()
    req_headers = app.current_request.headers
    if not verify_token(req_headers, req, config['signing_secret']):
        return 'Slack signing secret not valid'

    payload = slack_payload_extractor(req)

    logger.info(f'payload is: {payload}')

    action = Action(payload, config)

    action.perform_action()

    return ''
