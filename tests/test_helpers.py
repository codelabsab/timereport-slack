from chalicelib.lib.helpers import parse_date, date_range
from datetime import datetime
import pytest

format_str = "%Y-%m-%d"


def test_parse_date_today():
    today = datetime.now().strftime(format_str)

    today_test_dict = parse_date(date="today", format_str=format_str)
    assert isinstance(today_test_dict, dict)
    assert isinstance(today_test_dict["from"], datetime)
    assert isinstance(today_test_dict["to"], datetime)
    assert today == today_test_dict["from"].strftime(format_str)
    assert today == today_test_dict["to"].strftime(format_str)


def test_parse_date_invalid_format():
    empty_test_list = parse_date(date="not_supported_format")
    assert isinstance(empty_test_list, dict)
    assert empty_test_list == {"to": None, "from": None}


def test_parse_single_date():
    single_date = "2019-01-01"
    test_date = parse_date(date=single_date)

    assert isinstance(test_date, dict)
    assert test_date["from"] == datetime.strptime(single_date, "%Y-%m-%d")
    assert test_date["to"] == datetime.strptime(single_date, "%Y-%m-%d")


def test_parse_multiple_dates():
    first_date = "2019-01-01"
    second_date = "2019-02-01"
    multiple_dates = f"{first_date}:{second_date}"

    test_dates = parse_date(date=multiple_dates)
    assert isinstance(test_dates, dict)
    assert test_dates["from"] == datetime.strptime(first_date, "%Y-%m-%d")
    assert test_dates["to"] == datetime.strptime(second_date, "%Y-%m-%d")


def test_parse_invalid_multiple_dates():
    # First date is bigger than second date, which should result in an empty dict
    first_date = "2019-02-01"
    second_date = "2019-01-01"
    multiple_dates = f"{first_date}:{second_date}"

    test_dates = parse_date(date=multiple_dates)
    assert isinstance(test_dates, dict)
    assert test_dates["from"] is None
    assert test_dates["to"] is None


def test_invalid_date_format():
    invalid_format = "2019:01:02"
    test_date = parse_date(date=invalid_format)
    assert test_date["from"] is None
    assert test_date["to"] is None


def test_parse_today():
    test_date = parse_date(date="today")
    assert isinstance(test_date, dict)
    assert isinstance(test_date["from"], datetime)


def test_date_range():
    first_date = datetime.strptime("2019-01-01", format_str)
    second_date = datetime.strptime("2019-01-10", format_str)
    test_date_generator = date_range(start_date=first_date, stop_date=second_date)
    test_date_list = list(test_date_generator)
    assert len(test_date_list) == 10
    for item in test_date_list:
        assert isinstance(item, datetime)
