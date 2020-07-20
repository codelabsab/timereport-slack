import json
from datetime import datetime
import logging

log = logging.getLogger(__name__)


def create_lock(user_id, event_date):
    format_str = "%Y-%m"
    try:
        datetime.strptime(event_date, format_str)
    except ValueError:
        log.error(f"The event_date {event_date} isn't a valid format")
        return False

    event = {"user_id": user_id, "event_date": event_date}
    return event

