import os
import tests.test_data
import datetime
from timereport.lib.helpers import parse_config
from timereport.model import Dynamo
from timereport.lib.factory import factory
from timereport.lib.slack import slack_payload_extractor

dir_path = os.path.dirname(os.path.realpath(__file__))
test_config = parse_config(f'{dir_path}/config.json')
data = tests.test_data.add
payload = slack_payload_extractor(data)
events = factory(payload)

def test_parsing_config():

    assert test_config.get('SLACK_TOKEN') == 'fake token'
    assert test_config.get('db_url') == 'http://127.0.0.1:8000'
    assert test_config.get('aws_access_key_id') == 'my_access_key_id'
    assert test_config.get('aws_secret_access_key') == 'my_secret_access_key'

def test_payload():
    assert payload.get('token') == 'OwjK95k89vMbtbyvhvLZkXNl'
    assert payload.get('team_id') == 'CHANGEME'
    assert payload.get('team_domain') == 'codelabsab'
    assert payload.get('channel_id') == 'CA8THJML6'
    assert payload.get('channel_name') == 'development'
    assert payload.get('user_id') == 'U2FGC795G'
    assert payload.get('user_name') == 'kamger'
    assert payload.get('command') == '%2Fno-wsgi'
    assert payload.get('text') == 'add+vab+2018-12-01:2018-12-05'
    assert payload.get('response_url') == 'https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F491076166711%2FbVUlrKZrnElSOBUqn01FoxNf'
    assert payload.get('trigger_id') == '490225208629.83549292471.860541eab9e9c3c6d7464ea2e979c7a5'

def test_events():
    assert events[0].get('user_id') == 'U2FGC795G'
    assert events[0].get('event_date') == datetime.datetime(2018, 12, 1, 0, 0)
    assert events[0].get('user_name') == 'kamger'
    assert events[0].get('reason') == 'vab'
    assert events[0].get('hours') == '8'

def test_dynamodb_connection():
    db = Dynamo.EventModel
    db.Meta.host = test_config.get('db_url')
    # set aws credentials for tests (in production it will use IAM roles)
    db.Meta.aws_access_key_id = test_config.get('aws_access_key_id')
    db.Meta.aws_secret_access_key = test_config.get('aws_secret_access_key')

    # create the table
    if not db.exists():
        db.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    # create item
    for e in events:
        user_id = e.get('user_id')
        event_date = e.get('event_date')
        user_name = e.get('user_name')
        reason = e.get('reason')
        hours = e.get('hours')

        event = Dynamo.EventModel(hash_key=user_id, range_key=event_date)
        event.user_name = user_name
        event.reason = reason
        event.hours = hours
        # save tables to database
        event.save()

    event_date_start = events[0].get('event_date')
    event_date_end = events[2].get('event_date')

    result = []

    for i in db.scan((db.user_name == 'kamger') & (db.event_date.between(event_date_start, event_date_end))):
        result.append(i.attribute_values)

    assert len(result) == 3
