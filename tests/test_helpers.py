from chalicelib.lib.helpers import parse_date
from datetime import datetime
import pytest


def test_parse_date_today():
    format_str = '%Y-%m-%d'
    today = datetime.now().strftime(format_str)

    today_test_list = parse_date(date="today", format_str=format_str)
    assert isinstance(today_test_list, list)

    today_test = today_test_list.pop()
    assert isinstance(today_test, datetime)
    assert today == today_test.strftime(format_str)


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
    multiple_dates = "2019-01-01:2019-02-01"

    test_dates = parse_date(date=multiple_dates)
    assert isinstance(test_dates, list)
    assert len(test_dates) == 2
    assert isinstance(test_dates[0], datetime)
    assert isinstance(test_dates[1], datetime)