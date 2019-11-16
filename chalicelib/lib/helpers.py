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
    except (TypeError, ValueError) as error:
        log.error(f"Unable to validate date {date}. Error was: {error}")
        return False

    return True


def parse_date(date: str, format_str: str = "%Y-%m-%d") -> dict:
    """
    Parse the date from a string.
    Expects these formats:
    "today"
    "2019-01-01"
    "2019-01-01:2019-01-02"
    """

    dates = dict()
    if date == "today":
        dates["today"] = datetime.now()

    if ":" in date:
        first_date, second_date = date.split(":")

        if validate_date(first_date, format_str=format_str) and validate_date(second_date, format_str=format_str):
            if first_date > second_date:
                log.error(f"First date {first_date} needs to be smaller than second date {second_date}")
                return dates
            dates[f"{first_date}"] = datetime.strptime(first_date, format_str)
            dates[f"{second_date}"] = datetime.strptime(second_date, format_str)
    else:
        if validate_date(date, format_str=format_str):
            dates[f"{date}"] = datetime.strptime(date, format_str)

    return dates