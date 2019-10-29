from chalicelib.lib.timereport_api import api_v2 as api
from chalicelib.lib.interactive.helpers import date_range
from datetime import datetime


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
    fields = payload["original_message"]["attachments"][0]["fields"]

    # Create start and stop dates for range
    start = datetime.strptime(fields[2].get("value"), "%Y-%m-%d")
    stop = datetime.strptime(fields[3].get("value"), "%Y-%m-%d")

    # loop through date range and create events
    for date in date_range(start, stop):
        event = {
            "user_name": f"{fields[0].get('value')}",
            "reason": f"{fields[1].get('value')}",
            "event_date": f"{date.strftime('%Y-%m-%d')}",
            "hours": f"{fields[4].get('value')}",
        }
        r = api.create(url, event)
        res.append(r)

    return res


def interactive_delete(url: str, payload: dict) -> list:
    """
    Takes a payload and extracts user_id and date
    Calls backend api to delete all events for
    given user and date
    """

    # store responses
    # TODO: add support for ranges
    res = []

    user_id = (payload["user"]["id"],)
    date = payload["original_message"]["attachments"][0]["fields"][0].get("value")

    r = api.delete(url=url, user_id=user_id, date=date)

    # TODO: add support for ranges
    res.append(r)

    return res
