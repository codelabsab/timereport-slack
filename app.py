from chalice import Chalice
import os
import logging
from chalicelib.lib.interactive import interactive_handler
from chalicelib.lib.command import command_handler


# Set globals or die
TOKEN: str = f"{os.getenv('bot_access_token')}"
SECRET: str = f"{os.getenv('signing_secret')}"
API_URL: str = f"{os.getenv('backend_url')}"

# TODO: REASONS should load from env vars too
REASONS: tuple = ("vab", "sick", "intern", "vacation")

# Configure logger or die
logger = logging.getLogger()
logger.setLevel(os.getenv('log_level'))


app = Chalice(app_name='timereport')
app.debug = True


@app.route('/interactive', method='POST', content_types=['application/x-www-form-urlencoded'])
def interactive():
    return interactive_handler(app)


@app.route('/command', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def command():
    return command_handler(app)
