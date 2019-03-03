from ruamel.yaml import YAML
from datetime import datetime

yaml=YAML(typ='safe')


def parse_config(path='config.yaml'):
    """
    Parse config written in yaml
    :param path: the path to the config file. config.yaml is default
    :return: config
    """
    with open(path) as fd:
        config = yaml.load(fd)

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

def validate_year(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y')
        return True
    except:
        return False

def current_year():
    return datetime.utcnow().year
