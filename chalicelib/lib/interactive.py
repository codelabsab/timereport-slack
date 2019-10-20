from chalice import Chalice

from chalicelib.lib.slack import slack_payload_extractor
from chalicelib.lib.security import verify_token
from chalicelib.lib import api
from datetime import datetime, timedelta
from app import config


def date_range(start_date, stop_date):
    # TODO:
    #      Should be removed when we get correct data
    #      from command
    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta


def interactive_delete(url: str, payload: dict) -> list:
    """
    Takes a payload and extracts user_id and date
    Calls backend api to delete all events for
    given user and date
    """

    # store responses
    # TODO: add support for ranges
    res = []

    user_id = payload['user']['id'],
    date = payload['original_message']['attachments'][0]['fields'][0].get('value')

    r = api.delete(url=url, user_id=user_id, date=date)

    # TODO: add support for ranges
    res.append(r)

    return res


def interactive_add(url: str, payload: dict) -> list:
    """
    Creates events in the form of:
    event = {
            'user_name': "",
            'reason': f"{payload[1].get('value')}",
            'event_date': f"{date.strftime('%Y-%m-%d')}",
            'hours': f"{payload[4].get('value')}"
        }

    Sends events to backend api for persistent storage

    Example fields:

    fields:
    [
        {'title': 'User', 'value': 'test_user', 'short': False},
        {'title': 'Type', 'value': 'sick', 'short': False},
        {'title': 'Date start','value': '2019-09-28','short': False},
        {'title': 'Date end','value': '2019-09-28','short': False},
        {'title': 'Hours','value': '8','short': False}
    ]

    """

    # store responses
    res = []

    # extract fields context for easier processing and shorter lines :)
    fields = payload['original_message']['attachments'][0]['fields']

    # Create start and stop dates for range
    start = datetime.strptime(fields[2].get('value'), "%Y-%m-%d")
    stop = datetime.strptime(fields[3].get('value'), "%Y-%m-%d")

    # loop through date range and create events
    for date in date_range(start, stop):
        event = {
            'user_name': f"{fields[0].get('value')}",
            'reason': f"{fields[1].get('value')}",
            'event_date': f"{date.strftime('%Y-%m-%d')}",
            'hours': f"{fields[4].get('value')}"
        }
        r = api.create(url, event)
        res.append(r)

    return res


def interactive_handler(app: Chalice):
    """
    Extracts data from request and checks if
    users wants to submit or not.

    Routes payload data to correct function that
    mangles data to be sent before sending to backend api
    """

    # store backend url
    url = config['backend_url']

    # store headers, request and secret
    headers = app.current_request.headers
    request = app.current_request.raw_body.decode()
    # TODO: this should we a str: SECRET in app.py instead
    secret: str = config['signing_secret']

    # verify validity of request
    if not verify_token(headers, request, secret):
        return 'Slack signing secret not valid'

    # extract slack payload from request and store some vars
    payload = slack_payload_extractor(request)
    submit = payload.get('actions')[0].get('value')
    action = payload.get('callback_id')

    # did user press yes?
    if submit == "submit_yes":
        # is the action add?
        if action == 'add':
            # send fields to add function for further processing and before call to api lib
            results = interactive_add(url=url, payload=payload)
            for result in results:
                if result.status_code != 200:
                    # TODO: slack_client_block_responder("failed")
                    return ""
            # TODO: slack_client_block_responder("success")?
            return ""
        # or is the action delete?
        if action == 'delete':
            results = interactive_delete(url=url, payload=payload)
            for result in results:
                if result.status_code != 200:
                    # TODO: slack_client_block_responder("failed")
                    return ""
            # TODO: slack_client_block_responder("failed")
            return ""

    # user pressed no
    else:
        # TODO: slack_client_block_responder("cancelled")
        return ''
