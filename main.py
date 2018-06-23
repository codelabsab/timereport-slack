#!/usr/bin/env python
import os
import re
import datetime
import json

from dateutil.parser import parse
from flask import Flask, request, make_response, Response, jsonify
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from dotenv import load_dotenv, find_dotenv
from flaskext.mysql import MySQL


# load .env file with secrets
load_dotenv(find_dotenv())

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# MYSQL DB VALUES
MYSQL_DB_ENDPOINT = os.environ["MYSQL_DB_ENDPOINT"]
MYSQL_DB_NAME = os.environ["MYSQL_DB_NAME"]
MYSQL_DB_USER = os.environ["MYSQL_DB_USER"]
MYSQL_DB_PASSWORD = os.environ["MYSQL_DB_PASSWORD"]

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MYSQL_HOST'] = MYSQL_DB_ENDPOINT
app.config['MYSQL_USER'] = MYSQL_DB_USER
app.config['MYSQL_PASSWORD'] = MYSQL_DB_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB_NAME
mysql = MySQL()
mysql.init_app(app)

def validate(vacation_date):
    try:
        datetime.datetime.strptime(vacation_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")


@app.route("/slack/message_options", methods=['POST'])
def messoage_options():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])
    if request.form.get('token') == SLACK_VERIFICATION_TOKEN:
    # Dictionary of menu options which will be sent as JSON
        print(form_json)
        return Response(json.dumps(form_json), mimetype='application/json')

@app.route("/", methods=['POST'])
def parse_request():

    # Check to see if your team's token is the same, if not ignore the request
    if request.form.get('token') == SLACK_VERIFICATION_TOKEN:
        # save slack form responses
        channel = request.form.get('channel_name')
        username = request.form.get('user_name')
        text = request.form.get('text')
        command = request.form.get('command')
        response_url = request.form.get('response_url')
        trigger_id = request.form.get('trigger_id')

        # available options
        deviation_type = ["vab", "semester", "betald_sjukdag", "obetald_sjukdag", "ledigt", "semester", "foraldrar_ledigt" ]

        # split input into
        text_list = text.split(' ')
        if len(text_list) != 3:
            return "wrong number of args"

        vacation_type = text_list[0]
        vacation_date = text_list[1]
        vacation_hours = text_list[2]
        # validate input
        rex_vt = "^(%s)$" %('|'.join(deviation_type))
        rex_hours = "^[0-9]$"
        if not re.match(rex_vt, vacation_type):
            return "Wrong deviation type: [%s]\nChoose on of: %s" %(vacation_type, deviation_type) 
        elif vacation_date:
             try:
                 validate(vacation_date)
             except ValueError:
                 return "Not a valid date format: [%s]\nUse yyyy-mm-dd" %(vacation_date)
        elif not re.match(rex_hours, vacation_hours):
            return "Wrong hour: [%s]\nChoose single digit of [0-9]" %(vacation_hours)

        # create mysql connection
        #conn = mysql.connect()
        #cursor = conn.cursor()

        # create payload
        payload = {
        "text": "Timereport",
        "attachments": [
        {

            "text": "User %s\nType: %s\nDate: %s\nHours: %s" %(username, vacation_type, vacation_date, vacation_hours),
            "fallback": "Cant submit",
            "callback_id": "vacation",
            "color": "good",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "yes",
                    "text": "yes",
                    "type": "button",
                    "value": "yes"
                },
                {
                    "name": "no",
                    "text": "no",
                    "style": "danger",
                    "type": "button",
                    "value": "no",
                    "confirm": {
                        "title": "Submit?",
                        "text": "Send to db?",
                        "ok_text": "Yes",
                        "dismiss_text": "No"
                    }
                }
            ]
           }
         ]
        }
        #payload = { 
        #    "text": "User %s\nType: %s\nDate: %s\nHours: %s" %(username, vacation_type, vacation_date, vacation_hours)
        #}
        return jsonify(payload)

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/slack/events", app)

@app.route("/slack/events", methods=['POST'])
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if message.get("subtype") is None and "hi" in message.get('text'):
        channel = message["channel"]
        message = "Hello <@%s>! :tada:" % message["user"]
        CLIENT.api_call("chat.postMessage", channel=channel, text=message)

 
# Start the Flask server
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=os.environ["LISTEN_PORT"])
