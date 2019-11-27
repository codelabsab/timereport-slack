from chalicelib.lib.helpers import parse_date, date_range
from datetime import datetime
import pytest

format_str = "%Y-%m-%d"


def test_parse_date_today():
    today = datetime.now().strftime(format_str)

    today_test_list = parse_date(date="today", format_str=format_str)
    assert isinstance(today_test_list, list)
    assert len(today_test_list) == 1
    assert isinstance(today_test_list[0], datetime)
    assert today == today_test_list[0].strftime(format_str)


def test_parse_date_invalid_format():
    empty_test_list = parse_date(date="not_supported_format")
    assert isinstance(empty_test_list, list)
    assert empty_test_list == []


def test_parse_single_date():
    single_date = "2019-01-01"
    test_date = parse_date(date=single_date)

    assert isinstance(test_date, list)
    assert len(test_date) == 1
    assert isinstance(test_date[0], datetime)


def test_parse_multiple_dates():
    first_date = "2019-01-01"
    second_date = "2019-02-01"
    multiple_dates = f"{first_date}:{second_date}"

    test_dates = parse_date(date=multiple_dates)
    assert isinstance(test_dates, list)
    assert len(test_dates) == 2
    assert isinstance(test_dates[0], datetime)
    assert isinstance(test_dates[1], datetime)


def test_parse_invalid_multiple_dates():
    # First date is bigger than second date, which should result in an empty dict
    first_date = "2019-02-01"
    second_date = "2019-01-01"
    multiple_dates = f"{first_date}:{second_date}"

    test_dates = parse_date(date=multiple_dates)
    assert isinstance(test_dates, list)
    assert not test_dates


def test_invalid_date_format():
    invalid_format = "2019:01:02"
    test_date = parse_date(date=invalid_format)
    assert not test_date


def test_parse_today():
    test_date = parse_date(date="today")
    assert isinstance(test_date, list)
    assert isinstance(test_date[0], datetime)


def test_date_range():
    first_date = datetime.strptime("2019-01-01", format_str)
    second_date = datetime.strptime("2019-01-10", format_str)
    test_date_generator = date_range(start_date=first_date, stop_date=second_date)
    test_date_list = list(test_date_generator)
    assert len(test_date_list) == 10
    for item in test_date_list:
        assert isinstance(item, datetime)
