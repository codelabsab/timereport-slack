import os
import requests

from chalice import Chalice

from chalicelib.lib.slack import slack_payload_extractor, slack_responder, verify_token
from chalicelib.lib import api
from datetime import datetime, timedelta
from app import config


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
    secret: str = os.getenv("signing_secret")
    if not verify_token(headers, request, secret):
        return "Slack signing secret not valid"

    # extract slack payload from request and store some vars
    payload: dict = slack_payload_extractor(request)
    submit: str = payload.get("actions")[0].get("value")
    action: str = payload.get("callback_id")
    user_id: str = payload.get("user_id").get("id")

    # did user press yes?
    if submit == "submit_yes":
        # did user want to add?
        if action == "add":
            # send fields containing order to add function
            # for further processing and send to backend api
            url: str = config["backend_url"]
            fields: dict = payload["original_message"]["attachments"][0]["fields"]
            results: list = interactive_add(url=url, user_id=user_id, fields=fields)
            for result in results:
                if result.status_code != 200:
                    # slack_bot_responder here failed
                    return ""
                else:
                    # slack_bot_responder here success
                    return ""
        # or did user want to delete?
        if action == "delete":
            result = interactive_delete(url=url, payload=payload)
            if result.status_code != 200:
                # slack_bot_responder here failed
                return ""
            else:
                # slack_bot_responder here success
                return ""
    # user press no
    else:
        slack_responder(url=payload.get("response_url"), msg="Action canceled")
        return ""


def date_range(start_date, stop_date):
    # TODO:
    #      Should be removed when we get correct data
    #      from command
    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta


def interactive_delete(url, payload) -> requests.models.Response:
    """
    Takes a payload and extracts user_id and date
    Calls backend api to delete all events for
    given user and date
    """
    user_id = (payload["user"].get("id"),)
    date: str = payload["original_message"]["attachments"][0]["fields"][0].get("value")

    return api.delete_event(url=url, user_id=user_id, date=date)


def interactive_add(url: str, user_id: str, fields: dict) -> list:
    """
    This function takes a payload described in the form
    described below.

    Creates events in the form of:
    event = {
            'user_id': user_id,
            'user_name': f"{payload[0].get('value')}"
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

    res = []

    # create date range
    start = datetime.strptime(fields[2].get("value"), "%Y-%m-%d")
    stop = datetime.strptime(fields[3].get("value"), "%Y-%m-%d")

    for date in date_range(start, stop):
        event = {
            "user_id": user_id,
            "user_name": f"{fields[0].get('value')}",
            "reason": f"{fields[1].get('value')}",
            "event_date": f"{date.strftime('%Y-%m-%d')}",
            "hours": f"{fields[4].get('value')}",
        }
        res.append(api.create_event(url, event))

    return res
