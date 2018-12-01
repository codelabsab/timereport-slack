class Event(str):
    """
    expects structured data
    data =
      {'token': 'OwjK95k89vMbtbyvhvLZkXNl',
       'team_id': 'T2FG58LDV',
       'team_domain': 'codelabsab',
       'channel_id': 'CA8THJML6',
       'channel_name': 'development',
       'user_id': 'U2FGC795G',
       'user_name': 'kamger',
       'command': '%2Fno-wsgi',
       'text': 'add+vab+2018-10-01',
       'response_url': 'https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F491076166711%2FbVUlrKZrnElSOBUqn01FoxNf',
       'trigger_id': '490225208629.83549292471.860541eab9e9c3c6d7464ea2e979c7a5'
    }
    """

    def __init__(self, data):
        self.command = tuple(data['text'].split("+"))
        self.user_id: str = data['user_id']
        self.user_name: str = data['user_name']
        self.validate_command(self.cmd)

    def validate_command(self, command):
        try:
            if command[0] == "add":
                if command[1] in config['valid_reasons']:
                    self.date

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)