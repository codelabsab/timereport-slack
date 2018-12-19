from datetime import datetime, timedelta
from timereport.model import Event

def factory(order):
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
        for d in daterange(date_obj_start, date_obj_stop):
            dates.append(d)
    else:
        date_obj = datetime.strptime(date_str, format_str)
        dates.append(date_obj)


    for event_date in dates:
        # create dict
        order['action'] = action
        order['user_id'] = user_id
        order['user_name'] = user_name
        order['reason'] = reason
        order['event_date'] = event_date
        order['hours'] = hours
        e = Event.Event(**order)
        events.append(e)
    return events


def daterange(start_date, stop_date):
    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta