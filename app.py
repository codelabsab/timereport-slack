from chalice import Chalice
import os
import logging
from chalicelib.lib.helpers import parse_config
from chalicelib.lib.interactive import interactive_handler
from chalicelib.lib.command import command_handler


app = Chalice(app_name='timereport')
app.debug = True


logger = logging.getLogger()


dir_path = os.path.dirname(os.path.realpath(__file__))
config = parse_config(f'{dir_path}/chalicelib/config.yaml')
config['backend_url'] = os.getenv('backend_url')
config['bot_access_token'] = os.getenv('bot_access_token')
logger.setLevel(config['log_level'])


@app.route('/interactive', method='POST', content_types=['application/x-www-form-urlencoded'])
def interactive():
    return interactive_handler(app)


@app.route('/command', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def index():
    return command_handler(app)
