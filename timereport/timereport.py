#!/usr/bin/env python
import os
import datetime

from flask import Flask, request, make_response
from slackclient import SlackClient
from dotenv import load_dotenv, find_dotenv
from timereport.validators import validateDate, validateRegex


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

# global regex
date_regex_start = "([0-9]{4}-[0-9]{2}-[0-9]{2}|today)"
date_regex_end = ":([0-9]{4}-[0-9]{2}-[0-9]{2})?"
hour_regex = " ([0-9]) "
type_regex = "(vab|betald_sjukdag|obetald_sjukdag|ledig|semester|foraldrar_ledigt)"


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

def postMessage(channel_id, user_id, user_name, type_id, hours, date_start, date_end, attachment=None):
    if attachment is None:
        attachment=[
        {
            "fields": [
                {
                    "title": "User",
                    "value": "{}".format(user_name)
                },

                {
                    "title": "Type",
                    "value": "{}".format(type_id)
                },
                {
                    "title": "Date start",
                    "value": "{}".format(date_start)
                },
                {
                    "title": "Date end",
                    "value": "{}".format(date_end)
                },

                {
                    "title": "Hours",
                    "value": "{}".format(hours)
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

    slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            user=user_id,
            attachments=attachment
    )

@app.route("/", methods=["POST"])
def timereport():
    # save the token
    slack_token = request.form.get("token")
    # Verify that the request came from Slack
    verify_slack_token(slack_token)

    # assign the request values
    channel_id = request.form.get('channel_id')
    input_user_name = request.form.get('user_name')
    user_id = request.form.get('user_id')
    text = request.form.get('text')
    command = request.form.get('command')

    # the dialog to display if nothing or help was the input
    if "help" in text or len(text) == 0:
        help_menu=[
            {
            "color": "#3A6DE1",
            "pretext": "Help menu",
            "fields": [
                {
                    "title": "{} <type> <today> <hours|optional>".format(command),
                    "value": "create a deviation of <type> at <today>"

                },
		{
                    "title": "{} <type> <YYYY-MM-DD> <hours|optional>".format(command),
                    "value": "create a single day deviation of <type> at <date> <hours|optional>"
                },
                {
                    "title": "{} <type> <YYYY-MM-DD>:<YYYY-MM-DD|optional> <hours|optional>".format(command),
                    "value": "create a deviation of <type> at <start date>:<end date|optional> <hours|optional>"
                },

                {
                    "title": "Argument: <type>",
                    "value": "{}".format(type_regex)
                },
                {
                    "title": "Argument: <today|<YYYY-MM-DD>:<YYYY-MM-DD>",
                    "value": "<today> will set todays date or use <YYYY-MM-DD>:<YYYY-MM-DD> format to specify date start or optional date end range."
                },
                {
                    "title": "Argument: <hours|optional>",
                    "value": "<hours> will set number of hours.\nThis is optional and will default to 8 hours if not specified."
                }
            ],
            "footer": "Code Labs timereport",
            "footer_icon": "https://codelabs.se/favicon.ico",
            }
          ]

        postEphemeral(help_menu, channel_id, user_id)

    # use the global regex
    date_start = validateRegex(date_regex_start, text)
    date_end = validateRegex(date_regex_end, text)
    hours = validateRegex(hour_regex, text)
    type_id = validateRegex(type_regex, text)

    if 'empty' in date_start:
        # assume today's date
        date_start = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        # validate date
        validateDate(date_start)
    if 'empty' in date_end:
        # assign date_start to date_end
        date_end = date_start
    if 'empty' in hours:
        # assign 8 hours as default
        hours =  8
    if 'empty' in type_id:
        return make_response("wrong <type> argument. Allowed {}".format(type_regex, 200))

    # TODO BUILD USERNAME REGEX
    # capture the user name
    user_name_regex = "(?:{typid}).(?:{start}).(?:{end})?.(?:{hours})?(.*)".format(typid=type_id, start=date_start, end=date_end, hours=hours)
    user_name = validateRegex(user_name_regex, text)

    if 'empty' in user_name:
        user_name = input_user_name

    # post
    postMessage(channel_id, user_id, user_name, type_id, hours, date_start, date_end)

    # return ok here
    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=os.environ["LISTEN_PORT"])

