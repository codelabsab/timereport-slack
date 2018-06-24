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

# Helper for validating a date string
def validate(vacation_date):
    try:
        datetime.datetime.strptime(vacation_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")

# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)

# The endpoint Slack will send the user's menu selection to (Request URL)
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():

    # Save submissions to hash
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    # Set the values from the response and update the message accordingly
    message_type = form_json["type"]
    response_url = form_json["response_url"]
    user_id = form_json["user"]["id"]
    user_name = form_json["user"]["name"]
    channel_id = form_json["channel"]["id"]
    channel_name = form_json["channel"]["name"]

    if message_type == "dialog_submission":
        # save values from payload of dialog_submission type
        submission_deviation = form_json["submission"]["Deviation"]
        submission_month = form_json["submission"]["Month"]
        submission_day = form_json["submission"]["Day"]
        submission_hours = form_json["submission"]["Hours"]
        action_ts = form_json["action_ts"]
        if not re.match("^([1-8])$", submission_hours):
             error_payload = {
	         "errors": [
		    {
		     "name": "Hours",
		     "error": "Only digits between 1-8 allowed"
		    }
	         ]
             }
             return jsonify(error_payload)

        elif not re.match("^(3[01]|[12][0-9]|[1-9])$", submission_day):
             # todo validation of days
             error_payload = {
	         "errors": [
                    {
		    "name": "Day",
		    "error": "This is not a valid day. Only between 1-31 allowed"
		    }
	         ]
             }
             return jsonify(error_payload)
        else:
            # update user on progress
            slack_client.api_call(
              "chat.postEphemeral",
              channel=channel_id,
              user=user_id,
              attachments=[
            {
            "color": "#3A6DE1",
            "pretext": "Submitting to db...",
            "author_name": "User: {}".format(user_name),
            "fields": [
                {
                    "title": "Type",
                    "value": submission_deviation

                },
		{
                    "title": "Month",
                    "value": submission_month
                },
                {
                    "title": "Day",
                    "value": submission_day
                },
		{
                    "title": "Hours",
                    "value": submission_hours
                }
            ],
            "footer": "Code Labs timereport",
            "footer_icon": "https://codelabs.se/favicon.ico",
            "ts": action_ts
            }
          ]
        )
        return make_response("",200)
        ## SEND TO DB or CANCEL.
        ## UPDATE ON STATUS


    return make_response("", 200)

@app.route("/", methods=["POST"])
def timereport():
        # create mysql connection
#        #conn = mysql.connect()
#        #cursor = conn.cursor()
# A Dictionary of message attachment options
    VACATION_OPTIONS = {}
    # save the token
    slack_token = request.form.get("token")
    # Verify that the request came from Slack
    verify_slack_token(slack_token)

    # assign the request values
    channel_name = request.form.get('channel_id')
    user_id = request.form.get('user_id')
    text = request.form.get('text')
    command = request.form.get('command')
    response_url = request.form.get('response_url')
    trigger = request.form.get('trigger_id')
    # the dialog to display
    dialog = {
        "title": "Submit Timereport",
        "submit_label": "Submit",
        "callback_id": user_id + trigger,
        "elements": [
        {
            "label": "Deviation",
            "type": "select",
            "name": "Deviation",
            "placeholder": "Select a deviation type",
            "options": [
                {
                    "label": "vab",
                    "value": "vab"
                },
                {
                    "label": "semester",
                    "value": "semester"
                },
                {
                    "label": "betald sjukdag",
                    "value": "betald_sjukdag"
                },
                {
                    "label": "obetald sjukdag",
                    "value": "obetald_sjukdag"
                },
                {
                    "label": "ledig",
                    "value": "ledig"
                },
                {
                    "label": "foraldrar ledigt",
                    "value": "foraldrar_ledigt"
                }
            ]
        },
        {
            "label": "Month",
            "type": "select",
            "name": "Month",
            "placeholder": "Select a month",
            "options": [
                {
                    "label": "january",
                    "value": "january"
                },
                {
                    "label": "februari",
                    "value": "februari"
                },
                {
                    "label": "mars",
                    "value": "mars"
                },
                {
                    "label": "april",
                    "value": "april"
                },
                {
                    "label": "maj",
                    "value": "maj"
                },
                {
                    "label": "juni",
                    "value": "juni"
                },
                {
                    "label": "juli",
                    "value": "juli"
                },
                {
                    "label": "augusti",
                    "value": "augusti"
                },
                {
                    "label": "september",
                    "value": "september"
                },
                {
                    "label": "oktober",
                    "value": "oktober"
                },
                {
                    "label": "november",
                    "value": "november"
                },
                {
                    "label": "december",
                    "value": "december"
                },
        ]
        },
        {
            "label": "Day",
            "type": "text",
            "name": "Day",
            "placeholder": "Write the Day of month [1-31]"
       },
       {
            "label": "Hours",
            "type": "text",
            "name": "Hours",
            "placeholder": "Write your hours [1-8]"
        }
        ]
    }

    # save to OPTIONS
    slack_client.api_call(
    "dialog.open",
    trigger_id=trigger,
    dialog=dialog
    )
    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=os.environ["LISTEN_PORT"])
