import os

from chalice import Chalice

from chalicelib.lib.slack import slack_payload_extractor, slack_responder
from chalicelib.lib.security import verify_token
from chalicelib.lib import api
from datetime import datetime, timedelta


def interactive_handler(app: Chalice):
    """
    Extracts data from request and checks if
    users wants to submit or not.

    Passes payload to correct function that
    executes logic preparing data to be sent
    to backend api
    """

    # store headers and request
    headers = app.current_request.headers
    request = app.current_request.raw_body.decode()

    # verify validity of request
    secret = os.getenv('signing_secret')
    if not verify_token(headers, request, secret):
        return 'Slack signing secret not valid'

    # extract slack payload from request and store some vars
    payload = slack_payload_extractor(request)
    submit = payload.get('actions')[0].get('value')
    action = payload.get('callback_id')

    # did user press yes?
    if submit == "submit_yes":
        # did user want to add?
        if action == 'add':
            # send fields containing order to add function
            # for further processing and send to backend api
            interactive_add(
                payload['original_message']['attachments'][0]['fields']
            )
            # TODO:
            #      slack_responder here?
        # or did user want to delete?
        if action == 'delete':
            interactive_delete(payload)
            # TODO:
            #      slack_responder here?
    # user press no
    else:
        slack_responder(url=payload.get("response_url"), msg="Action canceled")
        return ''


def date_range(start_date, stop_date):
    # TODO:
    #      Should be removed when we get correct data
    #      from command
    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta


def interactive_delete(payload):
    """
    Takes a payload and extracts user_id and date
    Calls backend api to delete all events for
    given user and date
    """
    user_id = payload['user'].get('id'),
    date = payload['original_message']['attachments'][0]['fields'][0].get('value')
    api.delete(user_id, date)
    # TODO:
    #      should slack_respond here if successful?
    #      or let interactive_handler manage responses


def interactive_add(payload):
    """
    This function takes a payload described in the form
    described below.

    Creates events in the form of:
    event = {
            'user_name': "",
            'reason': f"{payload[1].get('value')}",
            'event_date': f"{date.strftime('%Y-%m-%d')}",
            'hours': f"{payload[4].get('value')}"
        }

    Sends events to backend api for persistent storage

    payload:
    [
                    {
                        'title': 'User',
                        'value': 'test_user',
                        'short': False
                    }, {
                        'title': 'Type',
                        'value': 'sick',
                        'short': False
                    }, {
                        'title': 'Date start',
                        'value': '2019-09-28',
                        'short': False
                    }, {
                        'title': 'Date end',
                        'value': '2019-09-28',
                        'short': False
                    }, {
                        'title': 'Hours',
                        'value': '8',
                        'short': False
                    }
                ]
    """
    start = datetime.strptime(payload[2].get('value'), "%Y-%m-%d")
    stop = datetime.strptime(payload[3].get('value'), "%Y-%m-%d")
    for date in date_range(start, stop):
        event = {
            'user_name': f"{payload[0].get('value')}",
            'reason': f"{payload[1].get('value')}",
            'event_date': f"{date.strftime('%Y-%m-%d')}",
            'hours': f"{payload[4].get('value')}"
        }
        api.create(event)
    # TODO:
    #      should slack_respond here if successful?
    #      or let interactive_handler manage responses



