import logging
from chalicelib.lib.list import get_between_date, get_user_by_id
from chalicelib.lib.slack import slack_responder

log = logging.getLogger(__name__)

class Action:
    
    def __init__(self, payload, config):
        self.payload = payload
        self.params = self.payload['text'][0].split()
        self.config = config
    

    def perform_action(self):
        self.action = self.params[0]
        self.response_url = self.payload['response_url'][0]
        self.user_id = self.payload['user_id'][0]

        if self.action == 'add':
            return self._add_action()
        
        if self.action == 'edit':
            pass

        if self.action == 'delete':
            pass
        
        if self.action == 'list':
            pass


    def _add_action(self):
        pass
    

    def _list_action(self):
        get_by_user = get_user_by_id(f"{self.config['backend_url']}/user", self.user_id)
        if isinstance(get_by_user, tuple):
            log.debug(f'Failed to return anything: {get_by_user[1]}')
        else:
            for r in get_by_user:
                slack_responder(self.response_url, f'```{str(r)}```')

        event_date = ''.join(self.params[-1:])
        if ':' in event_date:
            # temporary solution

            start_date, end_date = event_date.split(':')

            get_by_date = get_between_date(f"{self.config['backend_url']}/user/{self.user_id}", start_date, end_date)

            for r in get_by_date:
                slack_responder(self.response_url, f'```{str(r)}```')

        return ''


    def _delete_action(self):
        pass
    

    def _edit_action(self):
        pass