import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from chalicelib.lib.api import read_lock
from ruamel.yaml import YAML

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


def date_range(start_date: datetime, stop_date: datetime) -> List[datetime]:
    """
    A generator that yields the days between start_date and stop_date
    """

    delta = timedelta(days=1)
    while start_date <= stop_date:
        yield start_date
        start_date += delta


def month_range(start_date: datetime, end_date: datetime) -> List[date]:
    """
    A generator that yields the months between start_date and end_date
    """
    year = start_date.year
    month = start_date.month

    while True:
        current = date(year, month, 1)
        yield current
        if current.month == end_date.month and current.year == end_date.year:
            break
        month = ((month + 1) % 12) or 12
        if month == 1:
            year += 1


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


def validate_reason(config: Dict[str, Any], reason: str) -> bool:
    """
    Check that reason is valid
    """
    return reason in config.get("valid_reasons")


def parse_date(date: str, format_str: str = "%Y-%m-%d") -> dict:
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

    dates = {"to": None, "from": None}

    # handle aliases
    if date == "today":
        today = datetime.now()
        dates["from"] = today
        dates["to"] = today

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

        dates["from"] = datetime.strptime(date_from, format_str)
        dates["to"] = datetime.strptime(date_to, format_str)

    # handle single date
    else:
        if validate_date(date, format_str=format_str):
            dates["to"] = datetime.strptime(date, format_str)
            dates["from"] = datetime.strptime(date, format_str)

    return dates


def check_locks(
    config: Dict[str, Any], user_id: str, date: datetime, second_date: datetime
) -> list:
    """
    Get a list of locks for the specified user and daterange
    """
    dates_to_check = list()
    for date in date_range(start_date=date, stop_date=second_date):
        if not date.strftime("%Y-%m") in dates_to_check:
            dates_to_check.append(date.strftime("%Y-%m"))

    log.debug(f"Got {len(dates_to_check)} date(s) to check")
    response = read_lock(url=config["backend_url"], user_id=user_id)
    data = response.json()
    if not data:
        return []

    locked_dates = list()
    locked_months = [d["event_date"] for d in data]
    for date in dates_to_check:
        if date in locked_months:
            log.info(f"Date {date} is locked")
            dates_to_check.append(response.json())
            locked_dates.append(date)

    return locked_dates
