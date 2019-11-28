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


def date_range(start_date: datetime, stop_date: datetime) -> [datetime]:
    """
    A generator that yields the days between start_date and stop_date
    """

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


def parse_date(date: str, format_str: str = "%Y-%m-%d") -> list:
    """
    Parse the date from a string.
    Expects these formats:
    "today"
    "2019-01-01"
    "2019-01-01:2019-01-02"
    :returns:
             single -> list(date: datetime)
             range -> list(date_from: datetime, date_to: datetime)
    """

    dates = list()

    # handle aliases
    if date == "today":
        dates.append(datetime.now())

    # handle ranges
    elif ":" in date:
        try:
            date_from, date_to = date.split(":")
        except ValueError as error:
            log.error(f"unable to split date {date}. The error was: {error}")
            return dates

        if not validate_date(date_from, format_str=format_str):
            return dates

        if not validate_date(date_to, format_str=format_str):
            return dates

        if date_from > date_to:
            log.error(f"{date_from} is after {date_to}")
            return dates

        dates.append(datetime.strptime(date_from, format_str))
        dates.append(datetime.strptime(date_to, format_str))

    # handle single date
    else:
        if validate_date(date, format_str=format_str):
            dates.append(datetime.strptime(date, format_str))

    return dates
