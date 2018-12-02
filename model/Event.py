class Event:

    def __init__(self, user_id, user_name, reason, event_date, hours):
        self.user_id = user_id
        self.user_name = user_name
        self.reason = reason
        self.event_date = event_date
        self.hours = hours

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)
