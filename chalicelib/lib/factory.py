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

    fields = json_order["original_message"]["attachments"][0]["fields"]

    user_id = json_order["user"]["id"]
    user_name = fields[0]["value"]
    reason = fields[1]["value"]
    dates = parse_date(fields[2]["value"])
    hours = fields[3]["value"]

    events = []

    for date in date_range(start_date=dates["from"], stop_date=dates["to"]):
        log.info(f"date is {date}")
        document = {
            "user_name": user_name,
            "reason": reason,
            "event_date": date.strftime(format_str),
            "hours": hours,
            "user_id": user_id,
        }
        events.append(document)
    return events
