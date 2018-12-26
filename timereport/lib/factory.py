from datetime import datetime, timedelta
from timereport.model.event import create_event


def factory(order):
    """
    Create correct format from order
    :param order: The order object
    :return: list
    """
    format_str = "%Y-%m-%d"
    dates, events = [], []
    user_id, user_name = order['user_id'], order['user_name']
    cmd = order['text'].split("+")
    action, reason, date_str = cmd[:3]
    try:
        hours = cmd[3]
    except IndexError:
        hours = "8"
    if ":" in date_str:
        date_str_start, date_str_stop = date_str.split(":")
        date_obj_start = datetime.strptime(date_str_start, format_str)
        date_obj_stop = datetime.strptime(date_str_stop, format_str)
        for d in date_range(date_obj_start, date_obj_stop):
            dates.append(d)
    else:
        date_obj = datetime.strptime(date_str, format_str)
        dates.append(date_obj)
    for event_date in dates:
        e = create_event(user_id, user_name, reason, event_date, hours)
        events.append(e)
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
