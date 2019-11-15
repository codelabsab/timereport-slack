from ruamel.yaml import YAML
from datetime import timedelta, datetime
import logging

log = logging.getLogger(__name__)

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


def validate_date(date, format_str) -> bool:
    """
    Validate a string in date format is valid
    """

    try:
        datetime.strptime(date, format_str)
    except TypeError:
        return False

    return True


def parse_date(date: str, format_str: str = "%Y-%m-%d") -> list:
    """
    Parse the date from a string.
    Expects these formats:
    "today"
    "2019-01-01"
    "2019-01-01:2019-01-02"
    """

    date_list = list()
    if date == "today":
        date_list.append(datetime.now())
        return date_list

    if ":" in date:
        first_date, second_date = date.split(":")

        if validate_date(first_date, format_str=format_str) and validate_date(second_date, format_str=format_str):
            date_list.append(datetime.strptime(first_date, format_str))
            date_list.append(datetime.strptime(second_date, format_str))
    else:
        try:
            if validate_date(date, format_str=format_str):
                date_list.append(datetime.strptime(date, format_str))
        except ValueError as error:
            log.warning(f"Unable to get date from {date}. Error was: {error}")

    return date_list