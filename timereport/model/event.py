def create_event(user_id, user_name, reason, event_date, hours):
    event = {
        'user_id': user_id,
        'user_name': user_name,
        'reason': reason,
        'event_date': event_date,
        'hours': hours,
    }
    return event

