from chalicelib.lib import api
from chalicelib.lib.helpers import date_range
from datetime import datetime


def create_event(url: str, payload: dict) -> list:
    """
    Creates events in the form of:
    event = {
            'user_id': <user_id>
            'user_name': <user_name>,
            'reason': <reason>,
            'event_date': <date>,
            'hours': <hours>"
        }

    Sends events to backend api for persistent storage

    """

    # store responses
    res = []

    # prepare vars
    user_id: str = payload["user"]["id"]

    user_name: str = payload["original_message"]["attachments"][0]["fields"][0].get(
        "value"
    )

    reason: str = payload["original_message"]["attachments"][0]["fields"][1].get(
        "value"
    )

    hours: str = payload["original_message"]["attachments"][0]["fields"][4].get("value")

    # Create start and stop dates for range
    start: datetime = datetime.strptime(
        payload["original_message"]["attachments"][0]["fields"][2], "%Y-%m-%d"
    )
    stop: datetime = datetime.strptime(
        payload["original_message"]["attachments"][0]["fields"][3], "%Y-%m-%d"
    )

    # loop through date range and create events
    for date in date_range(start, stop):
        event = {
            "user_id": user_id,
            "user_name": user_name,
            "reason": reason,
            "event_date": f"{date.strftime('%Y-%m-%d')}",
            "hours": hours,
        }
        # store each event
        r = api.create_event(url=url, event=event)
        res.append(r)

    return res


def delete_event(url: str, payload: dict) -> list:
    """
    Takes a payload and extracts user_id and date
    Calls backend api to delete all events for
    given user and date
    """

    # store responses
    res = []

    user_id = payload["user"]["id"].get("value")
    date = payload["original_message"]["attachments"][0]["fields"][0].get("value")

    r = api.delete_event(url=url, user_id=user_id, date=date)

    res.append(r)

    return res
