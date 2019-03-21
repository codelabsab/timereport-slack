from datetime import datetime, timedelta
from ..model.event import Event

class EventFactory:
    """
    The EventFactory class can build event documents
    formt_str: The str format of dates. Defaults to '%Y-%m-%d'
    """

    def __init__(self, format_str="%Y-%m-%d"):
        self.format_str = format_str
        self.events = []

    def build(self, user_id, user_name, reason, date_str_from, date_str_to, hours=8):
        '''
        Expects valida data as:
        {
            user_id,
            user_name,
            reason,
            date_str_from,
            date_str_to,
            <hours>
        } 
        '''

        dates = []
        date_obj_from = datetime.strptime(date_str_from, self.format_str)
        date_obj_to = datetime.strptime(date_str_to, self.format_str)

        for d in EventFactory.date_range(date_obj_from, date_obj_to):
            dates.append(d)

        for date in dates:
            date_str = datetime.strftime(date, self.format_str)
            e = Event(user_id, user_name, reason, date_str, hours)
            self.events.append(e)

    @classmethod
    def date_range(self, date_from, date_to):
        delta = timedelta(days=1)
        while date_from <= date_to:
            yield date_from
            date_from += delta