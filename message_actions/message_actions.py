#!/usr/bin/env python
import os
import re
import json
import pandas as pd
import redis

from flask import Flask, request, make_response, jsonify, render_template
from flask_sessionstore import Session
from slackclient import SlackClient
from dotenv import load_dotenv, find_dotenv
from flask_pymongo import PyMongo
from requests import get

# load .env file with secrets
load_dotenv(find_dotenv())
finditer = re.finditer

# Your app's Slack bot user token
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]

# Slack client for Web API requests
slack_client = SlackClient(SLACK_BOT_TOKEN)

# redis db
REDIS_DB = os.environ['REDIS_DB']
REDIS_PORT = os.environ['REDIS_PORT']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = True
# session data
app.config['SESSION_TYPE'] = 'redis'
rdb = redis.Redis(host=REDIS_DB, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)
app.config['SESSION_REDIS'] = rdb
app.config['SESSION_EXPIRY_MINUTES'] = 60
app.config['SESSION_COOKIE_NAME'] = "session"
Session(app)

# MONGO DB VALUES
app.config['MONGO_HOST'] = os.environ["MONGO_HOST"]
app.config['MONGO_PORT'] = os.environ["MONGO_PORT"]
app.config['MONGO_USERNAME'] = os.environ["MONGO_USERNAME"]
app.config['MONGO_PASSWORD'] = os.environ["MONGO_PASSWORD"]
app.config['MONGO_DBNAME'] = os.environ["MONGO_DBNAME"]
app.config["MONGO_URI"] = "mongodb://{}:{}@{}:{}/{}".format(os.environ["MONGO_USERNAME"], os.environ["MONGO_PASSWORD"],
                                                            os.environ["MONGO_HOST"], os.environ["MONGO_PORT"],
                                                            os.environ["MONGO_DBNAME"])

mongo = PyMongo(app, connect=False)

# global regex
date_regex_start = "([0-9]{4}-[0-9]{2}-[0-9]{2}|today)"
date_regex_end = ":([0-9]{4}-[0-9]{2}-[0-9]{2})?"
hour_regex = " ([0-9]) "
type_regex = "(vab|betald_sjukdag|obetald_sjukdag|ledig|semester|foraldrar_ledigt)"

# hostname ip
my_ip = get('https://api.ipify.org').text


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
        attachments=[]  # empty `attachments` to clear the existing massage attachments
    )


def mongoSubmit(user_id, user_name, input_type_id, input_hours, input_date_start, input_date_end):
    insert = {
        "user_id": user_id,
        "user_name": user_name,
        "type_id": input_type_id,
        "hours": input_hours,
        "start": pd.to_datetime(input_date_start),
        "end": pd.to_datetime(input_date_end),
    }
    mongo.db.users.insert(insert)


    return "success"


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
        # save values type_id, date, hours
        selection = form_json["actions"][0]["value"]

        fields = form_json["original_message"]["attachments"][0]["fields"]

        input_user_name = fields[0]['value']

        input_type_id = fields[1]['value']

        input_date_start = fields[2]['value']

        input_date_end = fields[3]['value']

        input_hours = fields[4]['value']

        if selection == "submit_yes":
            # debug
            # print(input_date_start)
            # print(input_date_end)
            # submit to db
            # submit all ranges if multiple
            for t in pd.date_range(pd.to_datetime(input_date_start), pd.to_datetime(input_date_end)):
                mongoSubmit(user_id, input_user_name, input_type_id, input_hours, pd.to_datetime(t), input_date_end)

            chatUpdate(channel_id, message_ts, "submitted timereports successfully :thumbsup:", user_id)

            # Send an HTTP 200 response with empty body so Slack ktodays we're done here
            return make_response("", 200)
        else:
            return make_response("canceling...", 200)

    # Send an HTTP 200 response with empty body so Slack ktodays we're done here
    return make_response("", 200)


# Start the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ["LISTEN_PORT"])

