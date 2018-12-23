from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute

class EventModel(Model):
    """
    A DynamoDB Event Table
    """
    class Meta:
      table_name = "event"

    user_id = UnicodeAttribute(hash_key=True)
    event_date = UTCDateTimeAttribute(range_key=True)
    user_name = UnicodeAttribute()
    reason = UnicodeAttribute()
    hours = UnicodeAttribute()

    def get_all_data(self):
        event_data = {}
        event_data['user_id'] = self.event.user_id
        event_data['event_date'] = self.event.event_date
        event_data['user_name'] = self.event.user_name
        event_data['reason'] = self.event.reason
        event_data['hours'] = self.event.hours

        return event_data
