#!/usr/bin/env python
import os
import re
import datetime
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
try:
    get('https://api.ipify.org').text
except Exception as e:
    print("Error",e)
    my_ip = '0.0.0.0'
else:
    my_ip = get('https://api.ipify.org').text

def validateRDBConn():
    try:
        rdb.ping()
    except Exception as e:
        return "Error", e
    else:
        print("successful connection to rdb")


# Helper for validating a date string
def validateDate(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return ValueError("Invalid date, should be YYYY-MM-DD")


def validateRegex(regex, text):
    result = [i for i in finditer(regex, text) if i]
    if result:
        for match in result:
            return match.group(1)
    else:
        return ("empty")


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

def delRedisSession():
    # deletes keys in redis db
    for key in rdb.keys():
        rdb.delete(key)
    print("sessions deleted")

@app.route("/")
def main():
    return "hello world"

@app.route("/fetch", methods=["POST", "GET"])
def fetch():
    # validate redis db connection
    if validateRDBConn():
        # delete data here
        delRedisSession()
    if request.method == 'POST':
        # save the token
        slack_token = request.form.get("token")
        # Verify that the request came from Slack
        verify_slack_token(slack_token)
        # assign the request values
        channel_id = request.form.get('channel_id')
        user_id = request.form.get('user_id')
        input_user_name = request.form.get('user_name')
        text = request.form.get('text')
        command = request.form.get('command')

        if "help" in text or len(text) == 0:
            help_menu = [
                {
                    "color": "#3A6DE1",
                    "pretext": "Help menu",
                    "fields": [
                        {
                            "title": "{} (start:end) <YYYY-MM-01>:<YYYY-MM-01|optional> <user|optional>".format(
                                command),
                            "value": "fetch from database by providing 2018-05-01:2018-06-01 optional end date and optional username"

                        },
                        {
                            "title": "Argument: (start:end) <YYYY-03-01>:<YYYY-04-01>",
                            "value": "2018-03-01:2018-04-01 to query between a range or use only start month to query everything since start"
                        },
                        {
                            "title": "Argument: <user|optional>",
                            "value": "<user> will fetch data for specific user from database. If no user is specified then the querying username will be used"
                        }
                    ],
                    "footer": "Code Labs timereport",
                    "footer_icon": "https://codelabs.se/favicon.ico",
                }
            ]

            postEphemeral(help_menu, channel_id, user_id)
            return make_response("", 200)
        # use the global regex
        date_start = validateRegex(date_regex_start, text)
        date_end = validateRegex(date_regex_end, text)
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

        # TODO USERNAME REGEX
        user_name_regex = "(?:{typid})?.(?:{start}).(?:{end})?.(.*)".format(typid=type_id, start=date_start,
                                                                            end=date_end)

        user_name = validateRegex(user_name_regex, text)
        if 'empty' in user_name:
            user_name = input_user_name

        # validate the dates so they are real
        validateDate(date_start)
        validateDate(date_end)

        # convert to datetime
        start = pd.to_datetime(date_start)
        year = start.year
        month_start = start.month
        month_end = start.month + 1
        date_start = "{YYYY}-{MM}".format(YYYY=year, MM=month_start)
        date_end = "{YYYY}-{MM}".format(YYYY=year, MM=month_end)

        query = {"start": {"$gte": pd.to_datetime(date_start), "$lt": pd.to_datetime(date_end)}}

        # filter fields to not display : 0
        users = mongo.db.users.find(query, {"_id": 0, "user_id": 0, "end": 0})
        if not users.count():
            return make_response("Nothing found in database for {} {}".format(command, text))
        else:
            save_loop = []
            for u in users:
                # save_loop.append(text)
                save_loop.append(u)
                df = pd.DataFrame(save_loop)
                # re order columns
                frame = df[['user_name', 'type_id', 'start', 'hours']]

        # post it to slack
        slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            user=user_id,
            text="```" + frame.to_string(index=False, justify='center') + "```" + "http://{}:5000/data".format(my_ip)
        )

        # save query to redis
        validateRDBConn()
        rdb.set("data", frame.to_msgpack(compress='zlib'))

        return make_response("", 200)

# Start the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ["LISTEN_PORT"])

