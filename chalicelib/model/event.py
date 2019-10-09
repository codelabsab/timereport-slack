import logging
import json
log = logging.getLogger(__name__)


def create_event(user_id, user_name, reason, event_date, hours):
    format_str = "%Y-%m-%d"
    event = {
        'user_id': user_id,
        'user_name': user_name,
        'reason': reason,
        'event_date': event_date.strftime(format_str),
        'hours': hours,
    }
    return json.dumps(event)
