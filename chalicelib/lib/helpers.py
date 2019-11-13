from ruamel.yaml import YAML
from datetime import timedelta, datetime

yaml = YAML(typ="safe")


def parse_config(path="config.yaml"):
    """
    Parse config written in yaml
    :param path: the path to the config file. config.yaml is default
    :return: config
    """
    with open(path) as fd:
        config = yaml.load(fd)

    return config


def date_range(start_date, stop_date):
    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta


def validate_date(date) -> bool:

    format_str = "%Y-%m-%d"

    try:
        if ":" in date:
            start, stop = date.split(":")
            datetime.strptime(start, format_str)
            datetime.strptime(stop, format_str)
            if start > stop:
                return False
        else:
            datetime.strptime(date, format_str)
    except TypeError:
        return False

    return True
