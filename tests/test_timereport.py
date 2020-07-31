import os
import pytest
from chalicelib.lib.helpers import parse_config
from chalicelib.lib.factory import factory
from chalicelib.lib.list import get_list_data
from chalicelib.model.event import create_lock
from mockito import when, mock, unstub
import requests
from datetime import datetime
from .test_data import interactive_message

dir_path = os.path.dirname(os.path.realpath(__file__))
fake_user_url = "http://fake.nowhere/event/users/fake_userid"


def test_parsing_config():
    test_config = parse_config(f"{dir_path}/config.yaml")
    mandatory_options = ("log_level", "backend_url")
    for option in mandatory_options:
        assert isinstance(option, str)
        assert test_config.get(option) is not None


def test_get_list_data_default():
    month = datetime.now().strftime("%Y-%m")
    fake_response = "fake list data response"
    when(requests).get(
        url=fake_user_url, params={"startDate": f"{month}-01", "endDate": f"{month}-31"}
    ).thenReturn(mock({"status_code": 200, "text": fake_response}))
    test = get_list_data(
        url="http://fake.nowhere",
        user_id="fake_userid",
        date_str=datetime.now().strftime("%Y-%m"),
    )
    unstub()
    assert test == fake_response


def test_get_list_data_single_date():
    fake_response = "fake list data response"
    when(requests).get(
        url=fake_user_url, params={"startDate": "2019-01-01", "endDate": "2019-01-01"}
    ).thenReturn(mock({"status_code": 200, "text": fake_response}))
    test = get_list_data(
        url="http://fake.nowhere", user_id="fake_userid", date_str="2019-01-01"
    )
    unstub()
    assert test == fake_response


def test_get_list_data_date_range():
    fake_response = "fake list data response"
    when(requests).get(
        url=fake_user_url, params={"startDate": "2019-01-01", "endDate": "2019-01-02"}
    ).thenReturn(mock({"status_code": 200, "text": fake_response}))
    test = get_list_data(
        url="http://fake.nowhere",
        user_id="fake_userid",
        date_str="2019-01-01:2019-01-02",
    )
    unstub()
    assert test == fake_response


def test_get_list_data_month():
    fake_response = "fake list data response"
    when(requests).get(
        url=fake_user_url, params={"startDate": "2019-01-01", "endDate": "2019-01-31"}
    ).thenReturn(mock({"status_code": 200, "text": fake_response}))
    test = get_list_data(
        url="http://fake.nowhere", user_id="fake_userid", date_str="2019-01"
    )
    unstub()
    assert test == fake_response


def test_get_list_data_faulty_response():
    when(requests).get(
        url=fake_user_url, params={"startDate": "2019-01-01", "endDate": "2019-01-01"}
    ).thenReturn(mock({"status_code": 500}))
    test = get_list_data(
        url="http://fake.nowhere", user_id="fake_userid", date_str="2019-01-01"
    )
    unstub()
    assert test is False


def test_create_lock():
    test = create_lock(user_id="fake", event_date="2019-01")
    assert isinstance(test.get("event_date"), str)


def test_create_lock_faulty_date():
    test = create_lock(user_id="fake", event_date="invalid date string")
    assert test is not True


def test_factory():
    test_result = factory(json_order=interactive_message)
    assert isinstance(test_result, list)
    assert len(test_result) == 1
    assert isinstance(test_result[0], dict)
    for key in test_result[0]:
        assert test_result[0][key] is not None


def test_factory_faulty_date_format():
    with pytest.raises(TypeError):
        factory(json_order=interactive_message, format_str="faulty format")
