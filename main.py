#!/usr/bin/env python
import os

from flask import Flask, request, make_response, Response, jsonify
from slackclient import SlackClient
from dotenv import load_dotenv, find_dotenv

# load .env file with secrets
load_dotenv(find_dotenv())

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/vab', methods=['POST'])
def slash():
    if request.form['token'] == SLACK_VERIFICATION_TOKEN:
        payload = {'text': 'VAB slash command is successful!'}
        return jsonify(payload)


# Start the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
