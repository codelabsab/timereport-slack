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
from flask_pymongo import PyMongo

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

# MONGO DB VALUES
app.config['MONGO_HOST'] = os.environ["MONGO_HOST"]
app.config['MONGO_PORT'] = os.environ["MONGO_PORT"]
app.config['MONGO_USERNAME'] = os.environ["MONGO_USERNAME"]
app.config['MONGO_PASSWORD'] = os.environ["MONGO_PASSWORD"]
app.config['MONGO_DBNAME'] = os.environ["MONGO_DBNAME"]
mongo = PyMongo(app)

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

def postEphemeral(attachment, channel_id, user_id):
    slack_client.api_call(
            "chat.postEphemeral",
            channel=channel_id,
            user=user_id,
            attachments=attachment
    )

def dateNow():
    # create today's date stamp
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    date = "{:4d}-{:02d}-{:02d}".format(year, month, day)
    return date

@app.route("/", methods=["POST"])
def timereport():
    # save the token
    slack_token = request.form.get("token")
    # Verify that the request came from Slack
    verify_slack_token(slack_token)

    # assign the request values
    channel_id = request.form.get('channel_id')
    user_id = request.form.get('user_id')
    text = request.form.get('text')
    command = request.form.get('command')
    response_url = request.form.get('response_url')
    trigger = request.form.get('trigger_id')
    deviation_type = ["vab", "betald_sjukdag", "obetald_sjukdag", "ledig", "semester", "foraldrar_ledigt", "end" ]

    # split text arguments into list
    text_list = text.split(' ')

    # the dialog to display if nothing or help was the input
    if "help" in text_list[0] or not text:
        help_menu=[
            {
            "color": "#3A6DE1",
            "pretext": "Help menu",
            "fields": [
                {
                    "title": "{} <type> <now> <hours>".format(command),
                    "value": "create a single day deviation of <type> at this point in time"

                },
		{
                    "title": "{} <type> <YYYY-MM-DD> <hours>".format(command),
                    "value": "create a single day deviation of <type> at <date> <hours>"
                },
                {
                    "title": "Type:",
                    "value": "{}".format(deviation_type)
                }
            ],
            "footer": "Code Labs timereport",
            "footer_icon": "https://codelabs.se/favicon.ico",
            }
          ]

        postEphemeral(help_menu, channel_id, user_id)

    elif "now" in text_list[0]:
        # set date to now
        now = dateNow()
        # loop through deviation_type list and match against
        if len(text_list) != 3:
            return make_response("wrong number of arguments {} <now> <type> <hours>".format(command), 200)
        for dt in deviation_type:
            if dt in text_list[1]:
                type_id = dt
                break
            else:
                return make_response("wrong <type> argument: {}".format(text_list[1]), 200)
        # get hours from last argument proided
        hour_input = ''.join(text_list[-1:])
        if re.match('^[0-8]$', hour_input):
            hours = hour_input
        else:
            return make_response("wrong <hours> argument: {}".format(hour_input), 200)

        submit_menu=[
        {
            "fields": [
                {
                    "title": "Type: {}".format(type_id)
                },
                {
                    "title": "Date: {}".format(now)
                },
                {
                    "title": "Hours: {}".format(hours)
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

        postEphemeral(submit_menu, channel_id, user_id)

    # return ok here
    return make_response("", 200)

@app.route("/slack/message_actions", methods=["POST"])
def message_actions():

    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    # Check to see what the user's selection was and update the message accordingly
    # save values
    channel_id = form_json["channel"]["id"]
    message_ts = form_json["message_ts"]
    user_id = form_json["user"]["id"]
    print(channel_id)
    print(message_ts)
    print(user_id)
    print(json.dumps(form_json))
    if form_json["type"] == "interactive_message":
        selection = form_json["actions"][0]["value"]
        if selection == "submit_yes":
            # do DB stuff here
            print("doing database stuff")



            # update user with info if successfull
            slack_client.api_call(
                "chat.postEphemeral",
                channel=channel_id,
                user=user_id,
                response_type='ephemeral',
                replace_original='true',
                delete_original='true',
                text='submitted',
                attachment=[]
            )


        else:
            return make_response("canceling...", 200)

    else:
        print("regular message stuff")


    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=os.environ["LISTEN_PORT"])
