def createEvent(user_id, user_name, reason, event_date, hours):
    event = {}
    event['user_id'] = user_id
    event['user_name'] = user_name
    event['reason'] = reason
    event['event_date'] = event_date
    event['hours'] = hours
    return event

