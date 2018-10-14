#!/usr/bin/env python
import os
import urllib.parse
from pymongo import MongoClient
from bson import BSON, decode_all
from bson import Binary, Code
from bson.json_util import dumps, loads
from bson import json_util, ObjectId
import json

# MONGO DB VALUES
MONGO_HOST = os.environ["MONGO_HOST"]
MONGO_PORT = os.environ["MONGO_PORT"]
MONGO_USERNAME = os.environ["MONGO_USERNAME"]
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]
MONGO_DBNAME = os.environ["MONGO_DBNAME"]
MONGO_URI = "mongodb://{}:{}@{}:{}/{}".format(MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT, MONGO_DBNAME)

def lambda_handler(event, context):

  mongo = MongoClient(MONGO_URI)
  db = mongo[MONGO_DBNAME]

  # export prod collection
  with open('/tmp/users.bson', 'wb+') as f:
      for doc in db.users.find():
          f.write(BSON.encode(doc))

  # drop existing dev collection
  db.users_dev.drop()
  # import new from prod
  with open('/tmp/users.bson', 'rb') as f:
      db.users_dev.insert(decode_all(f.read()))
  mongo.close()
