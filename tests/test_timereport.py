import os
import pytest
from chalicelib.lib.helpers import parse_config
from chalicelib.lib.factory import factory
from chalicelib.lib.add import post_event
from chalicelib.lib.list import get_list_data
from chalicelib.model.event import create_lock
from mockito import when, mock, unstub
import requests
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
fake_user_url = "http://fake.nowhere/event/users/fake_userid"


def test_parsing_config():
    test_config = parse_config(f"{dir_path}/config.yaml")
    mandatory_options = ("log_level", "backend_url")
    for option in mandatory_options:
        assert isinstance(option, str)
        assert test_config.get(option) is not None


def test_create_event():
    fake_url = "http://fake.com"
    fake_data = "fake data"
    when(requests).post(
        url=fake_url, json=fake_data, headers={"Content-Type": "application/json"}
    ).thenReturn(mock({"status_code": 200}))
    response = post_event(fake_url, fake_data)
    assert response.status_code == 200
    unstub()


def test_create_event_failure():
    fake_url = "http://fake.com"
    fake_data = "fake data"
    when(requests).post(
        url=fake_url, json=fake_data, headers={"Content-Type": "application/json"}
    ).thenReturn(mock({"status_code": 500}))
    response = post_event(fake_url, fake_data)
    assert response.status_code != 200
    unstub()


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
