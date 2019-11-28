from datetime import datetime
from chalicelib.lib.helpers import date_range
from chalicelib.lib.helpers import parse_date
import logging

log = logging.getLogger(__name__)


def factory(json_order, format_str):
    """
    Extract necessary values from the interactive message sent via slack

    :param json_order: A dict based on slack interactive message payload
    :param format_str: datetime format
    :return: list
    """

    log.debug(f"json_order is: {json_order}")

    payload = json_order["original_message"]["attachments"][0]["fields"]

    user_name = payload[0]["value"]
    reason = payload[1]["value"]
    hours = payload[3]["value"]
    events = []
    dates = parse_date(payload[2]["value"])

    for date in date_range(start_date=dates["from"], stop_date=dates["to"]):
        log.info(f"date is {date}")
        document = {
            "user_name": user_name,
            "reason": reason,
            "event_date": date.strftime(format_str),
            "hours": hours,
        }
        events.append(document)
    return events
