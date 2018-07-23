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

@app.route("/", methods=["POST"])
def fetch():
    # save the token
    slack_token = request.form.get("token")
    # Verify that the request came from Slack
    verify_slack_token(slack_token)
    # assign the request values
    channel_id = request.form.get('channel_id')
    user_id = request.form.get('user_id')
    user_name = request.form.get('user_name')
    text = request.form.get('text')
    command = request.form.get('command')
    if text:
        text_list = text.split(' ')

    if "help" in text_list[0] or len(text) == 0:
        text_list = []
        help_menu=[
            {
            "color": "#3A6DE1",
            "pretext": "Timereport-fetch menu",
            "fields": [
                {
                    "title": "{} <YYYY-MM|optional> <user|optional>".format(command),
                    "value": "fetch from database by providing year month and username or nothing for all"

                },
		{
                    "title": "{} <YYYY-MM|optional> <all|optional>".format(command),
                    "value": "fetch from database all users for a specific month"
                },
                {
                    "title": "Argument: <YYYY-MM>",
                    "value": "2018-03 or empty for todays month as default value"
                },
                {
                    "title": "Argument: <user|optional>",
                    "value": "<user> will fetch data for specific user from database"
                }
            ],
            "footer": "Code Labs timereport",
            "footer_icon": "https://codelabs.se/favicon.ico",
            }
          ]

        postEphemeral(help_menu, channel_id, user_id)

    # probably <YYYY-MM> <user> provided
    if len(text_list) == 2:
        year = text_list[0].split('-')[0]
        month = text_list[0].split('-')[1]
        full_date = "{}-{}".format(year, month)
        user = text_list[1] # save user second argument
        if user == "all":
            mongo_query = { "date.date_month": month, "date.date_year": year }
        else:
            mongo_query = { "date.date_month": month, "date.date_year": year, "user_name": user }
     # are we providing <YYYY-MM> or <user>
    elif len(text_list) == 1:
        date = dateToday()
        year = date.split('-')[0]
        month = date.split('-')[1]
        # date first argument
        if re.match('^[0-9][0-9][0-9][0-9]-[0-9][0-9]$', text_list[0]):
            year = text_list[0].split('-')[0]
            month = text_list[0].split('-')[1]
            full_date = "{}-{}".format(year, month)
        # username first argument
        elif text_list[0] == user_name:
            # fetch todays month entries
            mongo_query = { "date.date_month": month, "date.date_year": year, "user_name": user_name }
        # if argument is date format only fetch for this month
        else:
            mongo_query = { "date.date_month": month, "date.date_year": year, "user_name": text_list[0] }
    else:
        return make_response("", 200)
        date = dateToday()
        year = date.split('-')[0]
        month = date.split('-')[1]
   #     mongo_query = { "date.date_month": month, "date.date_year": year }
   #     full_date = "{}-{}".format(year, month)


    full_date = "{}-{}".format(year, month)
    try:
        mongo_query
    except NameError:
        mongo_query = { "date.date_month": month, "date.date_year": year }
    mongo_filter = { "user_name": 1, "date.date": 1, "type_id": 1, "hours": 1, "_id": 0 }
    users = mongo.db.users.find(mongo_query , mongo_filter)
    if users.count() >= 1:
        for u in users:
            date = u['date']['date']
            hours = u['hours']
            type_id = u['type_id']
            user_name = u['user_name']
            text = "*****Values for {} ******\nUser: {}\nDate: {}\nType: {}\nHours: {}".format(full_date,user_name,date,type_id,hours)
            print("*****Values for {} ******\nUser: {}\nDate: {}\nType: {}\nHours: {}".format(full_date,user_name,date,type_id,hours))
            slack_client.api_call(
                "chat.postMessage",
                channel=channel_id,
                user=user_id,
                text=text
            )
    else:
        return make_response("Nothing found in database for {} {}".format(command, text))

    return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=os.environ["LISTEN_PORT"])
