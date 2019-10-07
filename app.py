from chalice import Chalice
import os
import logging
from chalicelib.lib.slack import (slack_payload_extractor, verify_token)
from chalicelib.lib.helpers import parse_config
from chalicelib.action import Action
from chalicelib.lib.interactive import interactive_handler


app = Chalice(app_name='timereport')
app.debug = True


logger = logging.getLogger()


dir_path = os.path.dirname(os.path.realpath(__file__))
config = parse_config(f'{dir_path}/chalicelib/config.yaml')
config['backend_url'] = os.getenv('backend_url')
config['bot_access_token'] = os.getenv('bot_access_token')
config['signing_secret'] = os.getenv('signing_secret')
logger.setLevel(config['log_level'])


@app.route('/interactive', method='POST', content_types=['application/x-www-form-urlencoded'])
def interactive():
    return interactive_handler(app.current_request.raw_body.decode())


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
