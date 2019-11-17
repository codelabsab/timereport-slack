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

    dates = list()
    if date == "today":
        dates.append(datetime.now())

    if ":" in date:
        try:
            first_date, second_date = date.split(":")
        except ValueError as error:
            log.error(f"Unable to split date {date}. The error was: {error}")
            return dates

        if validate_date(first_date, format_str=format_str) and validate_date(second_date, format_str=format_str):
            if first_date > second_date:
                log.error(f"First date {first_date} needs to be smaller than second date {second_date}")
                return dates

            dates.append(datetime.strptime(first_date, format_str))
            dates.append(datetime.strptime(second_date, format_str))
    else:
        if validate_date(date, format_str=format_str):
            dates.append(datetime.strptime(date, format_str))

    return dates


def get_dates(first_date: datetime, second_date: datetime = None, format_str: str = "%Y-%m") -> list:
    """
    Get all dates between two dates that matches the date format string.
    """

    dates = list()

    if not second_date:
        dates.append(first_date.strftime('%Y-%m'))
        return dates

    delta = second_date - first_date

    for delta in range(delta.days + 1):
        date = first_date + timedelta(days=delta)
        if date.strftime(format_str) not in dates:
            dates.append(date.strftime(format_str))

    return dates