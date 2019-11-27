import json
from datetime import datetime
import logging

log = logging.getLogger(__name__)


def create_event(user_id, user_name, reason, event_date, hours):
    format_str = "%Y-%m-%d"
    event = {
        "user_id": user_id,
        "user_name": user_name,
        "reason": reason,
        "event_date": event_date.strftime(format_str),
        "hours": hours,
    }
    return event


def create_lock(user_id, event_date):
    format_str = "%Y-%m"
    try:
        datetime.strptime(event_date, format_str)
    except ValueError:
        log.error(f"The event_date {event_date} isn't a valid format")
        return False

    event = {"user_id": user_id, "event_date": event_date}
    return event


class Event:
    # Work in progress, not used.

    def __init__(self, user_id, user_name, reason, event_date, hours, fmt):
        self.user_id = user_id
        self.user_name = user_name
        self.reason = reason
        self.event_date = event_date
        self.hours = hours
        self.fmt = fmt

    def to_json(self):
        return json.dumps(vars(self))
