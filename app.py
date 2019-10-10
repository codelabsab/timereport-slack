from chalice import Chalice
import os
import json
import logging

from chalicelib.lib.factory import factory, json_factory
from chalicelib.lib.add import post_event
from chalicelib.lib.delete import delete_event
from chalicelib.lib.slack import (slack_payload_extractor, submit_message_menu,
                                  delete_message_menu, verify_token, Slack)

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
slack = Slack(slack_token=config["bot_access_token"])

@app.route('/interactive', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def interactive():
    req = app.current_request.raw_body.decode()
    payload = slack_payload_extractor(req)
    selection = payload.get('actions')[0].get('value')
    logger.info(f"Selection is: {selection}")
    slack_response_message = "Action canceled :x:"
    user_id = None

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
                slack_response_message = 'Got unexpected response from backend'
            else:
                slack_response_message = f'successfully deleted entry: {date}'

            slack.client.chat_postMessage(
                channel=user_id,
                text=slack_response_message,
            )
            return ''

        if payload.get('callback_id') == 'add':
            slack_response_message = 'Added successfully :white_check_mark:'
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
                slack_response_message = (
                    f"Successfully added {len(events) - len(failed_events)} events.\n"
                    f"These however failed: ```{failed_events} ```"
                )
    
    slack.client.chat_postMessage(
        channel=user_id,
        text=slack_response_message,
    )
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
