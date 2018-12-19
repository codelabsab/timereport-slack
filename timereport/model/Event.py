class Event:
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.user_name = kwargs.get('user_name')
        self.reason = kwargs.get('reason', 'add')
        self.event_date = kwargs.get('event_date', '2018-09-11')
        self.hours = kwargs.get('hours')

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)
