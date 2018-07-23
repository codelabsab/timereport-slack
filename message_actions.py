#!/usr/bin/env python
import os
import re
import datetime
import json

from pprint import pprint
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
app.config["MONGO_URI"] = "mongodb://{}:{}@{}:{}/{}".format(os.environ["MONGO_USERNAME"], os.environ["MONGO_PASSWORD"], os.environ["MONGO_HOST"], os.environ["MONGO_PORT"], os.environ["MONGO_DBNAME"])

mongo = PyMongo(app, connect=False)

# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)

def chatUpdate(channel_id, message_ts, text, user_id):
    slack_client.api_call(
              "chat.update",
              channel=channel_id,
              ts=message_ts,
              text="<@{}> {}".format(user_id, text),
              attachments=[] # empty `attachments` to clear the existing massage attachments
    )

def mongoSubmit(user_id, user_name, input_type_id, input_hours, input_date, input_date_end=None):
    # strip date into smaller chunks
    date_year = input_date.split('-')[0]
    date_month = input_date.split('-')[1]
    date_day = input_date.split('-')[2]

    # set to start date if end is not given
    if input_date_end is None:
        date_end = input_date
        date_month_end = date_month
        date_day_end = date_day

    return mongo.db.users.insert(
    {
        "user_id": user_id,
        "user_name": user_name,
        "type_id": input_type_id,
        "hours": input_hours,
        "date": {
            "date": input_date,
            "date_end": date_end,
            "date_year": date_year,
            "date_month": date_month,
            "date_month_end": date_month_end,
            "date_day": date_day,
            "date_day_end": date_day_end
        }
    })

@app.route("/", methods=["POST"])
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
    user_name = form_json['user']['name']

    if form_json["type"] == "interactive_message":
        # save values
        selection = form_json["actions"][0]["value"]
        input_type_id = json.dumps(form_json["original_message"]["attachments"][0]["fields"][0]["value"]).strip('"')
        input_hours = json.dumps(form_json["original_message"]["attachments"][0]["fields"][2]["value"]).strip('"')
        input_date = json.dumps(form_json["original_message"]["attachments"][0]["fields"][1]["value"]).strip('"')
        date_month = input_date.split('-')[1]

        if selection == "submit_yes":
            # do DB stuff here
            print("doing database stuff")
            print("user_id: {}\n user_name: {}\n, input_type_id: {}\n, input_hours: {}\n, input_date: {}\n".format(repr(user_id), repr(user_name), repr(input_type_id), repr(input_hours), repr(input_date)))
            mongoSubmit(user_id, user_name, input_type_id, input_hours, input_date)
            users = mongo.db.users.find({ "date.date_year": "2018", "date.date_month": "03" })
            for u in users:
                pprint(u)

            chatUpdate(channel_id, message_ts, "submitted timereports successfully :thumbsup:", user_id)

            # Send an HTTP 200 response with empty body so Slack ktodays we're done here
            return make_response("", 200)


        else:
            return make_response("canceling...", 200)

    else:
        print("regular message stuff")


    # Send an HTTP 200 response with empty body so Slack ktodays we're done here
    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=os.environ["LISTEN_PORT"])
