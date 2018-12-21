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
