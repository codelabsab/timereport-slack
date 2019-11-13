from datetime import datetime, timedelta
from ..model.event import create_event
from chalicelib.lib.helpers import date_range
import logging

log = logging.getLogger(__name__)


def factory(json_order, format_str):
    """
    Extract necessary values from the interactive message sent via slack

    :param json_order: A dict based on slack interactive message payload
    :return: list
    """

    log.debug(f"json_order is: {json_order}")

    payload = json_order["original_message"]["attachments"][0]["fields"]

    user_name = payload[0]["value"]
    reason = payload[1]["value"]
    date = payload[2]["value"]
    hours = payload[3]["value"]
    events = []

    start_date = date
    stop_date = date
    if ":" in date:
        start_date, stop_date = date.split(":")

    date_obj_start = datetime.strptime(start_date, format_str)
    date_obj_stop = datetime.strptime(stop_date, format_str)
    for date in date_range(date_obj_start, date_obj_stop):
        log.info(f"date is {date}")
        document = {
            "user_name": user_name,
            "reason": reason,
            "event_date": date.strftime(format_str),
            "hours": hours,
        }
        events.append(document)
    return events
