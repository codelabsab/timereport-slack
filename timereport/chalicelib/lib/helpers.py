import json


def parse_config(path='config.json'):
    """
    Parse config written in json
    :param path: the path to the config file. config.json is default
    :return: config
    """
    with open(path) as fd:
        config = json.load(fd)

    return config


def verify_reasons(valid_reasons, reason):
    if reason in valid_reasons:
        return True
    else:
        return False


def verify_actions(valid_actions, action):
    if action in valid_actions:
        return True
    else:
        return False
