from chalicelib.lib.helpers import parse_date, get_dates
from datetime import datetime
import pytest

format_str = '%Y-%m-%d'

def test_parse_date_today():
    today = datetime.now().strftime(format_str)

    today_test_dict = parse_date(date="today", format_str=format_str)
    assert isinstance(today_test_dict, dict)

    today_test = today_test_dict.get('today')
    assert isinstance(today_test, datetime)
    assert today == today_test.strftime(format_str)


def test_parse_date_invalid_format():
    empty_test_list = parse_date(date="not_supported_format")
    assert isinstance(empty_test_list, dict)
    assert empty_test_list == {}


def test_parse_single_date():
    single_date = "2019-01-01"
    test_date = parse_date(date=single_date)

    assert isinstance(test_date, dict)
    assert len(test_date.keys()) == 1
    assert isinstance(test_date.get(single_date), datetime)


def test_parse_multiple_dates():
    first_date = "2019-01-01"
    second_date = "2019-02-01"
    multiple_dates = f"{first_date}:{second_date}"

    test_dates = parse_date(date=multiple_dates)
    assert isinstance(test_dates, dict)
    assert len(test_dates.keys()) == 2
    assert isinstance(test_dates[first_date], datetime)
    assert isinstance(test_dates[second_date], datetime)


def test_parse_invalid_multiple_dates():
    # First date is bigger than second date, which should result in an empty dict
    first_date = "2019-02-01"
    second_date = "2019-01-01"
    multiple_dates = f"{first_date}:{second_date}"

    test_dates = parse_date(date=multiple_dates)
    assert isinstance(test_dates, dict)
    assert not test_dates


def test_get_dates_in_range():
    first_date = datetime.strptime("2019-01-01", format_str)
    second_date = datetime.strptime("2019-02-01", format_str)
    test_date_range = get_dates(first_date=first_date, second_date=second_date)
    assert isinstance(test_date_range, list)
    assert test_date_range[0] == "2019-01"
    assert test_date_range[1] == "2019-02"


def test_get_dates_single():
    first_date = datetime.strptime("2019-01-01", format_str)
    test_date_range = get_dates(first_date=first_date)
    assert isinstance(test_date_range, list)
    assert test_date_range[0] == "2019-01"


def test_invalid_date_format():
    invalid_format = "2019:01:02"
    test_date = parse_date(date=invalid_format)
    assert not test_date