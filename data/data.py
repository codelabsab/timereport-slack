#!/usr/bin/env python
import os
import pandas as pd
import redis

from flask import Flask, request, make_response, jsonify, render_template
from flask_sessionstore import Session
from dotenv import load_dotenv, find_dotenv


# load .env file with secrets
load_dotenv(find_dotenv())

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


@app.route("/", methods=["GET"])
def data():
    # Set CSS properties for th elements in dataframe
    try:
        rdb.get("data")
        data = pd.read_msgpack(rdb.get("data"))
        return render_template('index.html', data=data.to_html(index=False, justify='center', classes="table table-striped"))
    except Exception as e:
        return render_template('index.html', data="<p>no data found</p><br/>Exception: " + str(e) + "<p></br></br>run /timereport-fetch in slack first</p></br>")


# Start the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0")

