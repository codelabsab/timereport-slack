from datetime import datetime, timedelta
from ..model.event import create_event
import logging

log = logging.getLogger(__name__)


def factory(order):
    """
    Create correct format from order
    :param order: The order object
    :return: list
    """
    format_str = "%Y-%m-%d"
    dates, events = [], []
    user_id, user_name = order['user_id'], order['user_name']

    cmd = order['text'][0].split()

    if len(cmd) < 3 or len(cmd) > 4:
        return False

    reason, date_str = cmd[1:3]
    log.debug(f"Date string is: {date_str}")

    try:
        hours = round(float(cmd[3]), 1)
        if 0 < hours > 8:
            hours = 8
    except IndexError:
        hours = 8

    except ValueError:
        return False

    if ":" in date_str:
        date_str_start, date_str_stop = date_str.split(":")
        date_obj_start = datetime.strptime(date_str_start, format_str)
        date_obj_stop = datetime.strptime(date_str_stop, format_str)
        for d in date_range(date_obj_start, date_obj_stop):
            dates.append(d)
    elif "today" in date_str:
        date_obj = datetime.now().date()
        dates.append(date_obj)
    else:
        log.debug(f"Will try to convert string {date_str} to a datetime object")
        date_obj = datetime.strptime(date_str, format_str)
        dates.append(date_obj)

    for event_date in dates:
        e = create_event(user_id, user_name, reason, event_date, hours)
        events.append(e)
    return events


def json_factory(json_order):
    '''[{
                    "title": "User",
                    "value": "kamger",
                    "short": false
                }, {
                    "title": "Type",
                    "value": "vab",
                    "short": false
                }, {
                    "title": "Date start",
                    "value": "2018-12-03",
                    "short": false
                }, {
                    "title": "Date end",
                    "value": "2018-12-05",
                    "short": false
                }, {
                    "title": "Hours",
                    "value": "2018-12-05",
                    "short": false
                }]



                '''
    format_str = "%Y-%m-%d"

    payload = json_order['original_message']['attachments'][0]['fields']

    user_id = json_order['user']['id']
    user_name = payload[0]['value']
    reason = payload[1]['value']
    start_date = payload[2]['value']
    stop_date = payload[3]['value']
    hours = payload[4]['value']
    events = []
    date_obj_start = datetime.strptime(start_date, format_str)
    date_obj_stop = datetime.strptime(stop_date, format_str)
    for date in date_range(date_obj_start, date_obj_stop):
        log.info(f'date is {date}')
        document = {
            'user_id': user_id,
            'user_name': user_name,
            'reason': reason,
            'event_date': date.strftime(format_str),
            'hours': hours,
        }
        events.append(document)
    return events

def date_range(start_date, stop_date):
    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta


def date_to_string(date):
    format_str = "%Y-%m-%d"
    return datetime.strftime(date, format_str)


def json_serial(date):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(date, (datetime, datetime.date)):
        return date.isoformat()
    raise TypeError ("Type %s not serializable" % type(date))
