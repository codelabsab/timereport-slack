from chalicelib.lib.helpers import parse_date
from datetime import datetime
import pytest


def test_parse_date_today():
    format_str = '%Y-%m-%d'
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