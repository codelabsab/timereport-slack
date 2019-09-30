import os
import pytest
from chalicelib.lib.helpers import parse_config
from chalicelib.lib.factory import factory, json_factory, date_to_string
from chalicelib.lib.add import post_event
from chalicelib.lib.list import get_list_data
from chalicelib.model.event import create_lock
from mockito import when, mock, unstub
import botocore.vendored.requests.api as requests
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
fake_user_url = "http://fake.nowhere/event/users/fake_userid"

def test_parsing_config():
    test_config = parse_config(f"{dir_path}/config.yaml")
    mandatory_options = ("log_level", "backend_url")
    for option in mandatory_options:
        assert isinstance(option, str)
        assert test_config.get(option) is not None


@pytest.mark.parametrize(
    "date_string",
    ["2018-01-01", "today", "today 8", "today 24", "2019-01-01:2019-02-01"],
)
def test_factory(date_string):
    fake_order = dict(
        user_id="fake",
        user_name="fake mcFake",
        text=[f"fake_cmd=do_fake fake_reason {date_string}"],
    )

    fake_result = factory(fake_order)
    assert isinstance(fake_result, list)
    test_data = fake_result.pop()
    assert isinstance(test_data.get("event_date"), str)
    for item in ("user_id", "user_name", "reason"):
        assert isinstance(test_data[item], str)

    assert int(test_data["hours"]) <= 8


def test_wrong_hours_data_type():
    fake_order = dict(
        user_id="fake",
        user_name="fake mcFake",
        text=[f"fake_cmd=do_fake fake_reason today wrong_hours"],
    )
    assert factory(fake_order) is False


@pytest.mark.parametrize(
    "args_list", [["one", "two", "three", "four", "five"], ["one_argument"]]
)
def test_wrong_number_of_args_for_add(args_list):
    fake_order = dict(user_id="fake", user_name="fake mcFake", text=args_list)
    assert factory(fake_order) is False


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


def test_json_factory():
    from .test_data import interactive_message

    fake_result = json_factory(interactive_message)
    assert isinstance(fake_result, list)
    for item in ("user_name", "reason", "event_date", "hours"):
        assert item in fake_result[0]


def test_date_to_string():
    test_data = date_to_string(datetime.now())
    assert isinstance(test_data, str)


def test_get_list_data_default():
    month = datetime.now().strftime("%Y-%m") 
    fake_response = "fake list data response"
    when(requests).get(
        url=fake_user_url,
        params={
            'startDate': f"{month}-01",
            'endDate': f"{month}-31"
        }
    ).thenReturn(mock({"status_code": 200, "text": fake_response}))
    test = get_list_data(
        url="http://fake.nowhere", user_id="fake_userid", date_str=datetime.now().strftime("%Y-%m")
    )
    unstub()
    assert test == fake_response


def test_get_list_data_single_date():
    fake_response = "fake list data response"
    when(requests).get(
        url=fake_user_url,
        params={"startDate": "2019-01-01", "endDate": "2019-01-01"},
    ).thenReturn(mock({"status_code": 200, "text": fake_response}))
    test = get_list_data(
        url="http://fake.nowhere", user_id="fake_userid", date_str="2019-01-01"
    )
    unstub()
    assert test == fake_response


def test_get_list_data_date_range():
    fake_response = "fake list data response"
    when(requests).get(
        url=fake_user_url,
        params={"startDate": "2019-01-01", "endDate": "2019-01-02"},
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
        url=fake_user_url,
        params={"startDate": "2019-01-01", "endDate": "2019-01-31"},
    ).thenReturn(mock({"status_code": 200, "text": fake_response}))
    test = get_list_data(
        url="http://fake.nowhere",
        user_id="fake_userid",
        date_str="2019-01",
    )
    unstub()
    assert test == fake_response


def test_get_list_data_faulty_response():
    when(requests).get(
        url=fake_user_url,
        params={
            'startDate': "2019-01-01",
            'endDate': "2019-01-01",
        }
    ).thenReturn(mock({"status_code": 500}))
    test = get_list_data(url="http://fake.nowhere", user_id="fake_userid", date_str="2019-01-01")
    unstub()
    assert test is False


def test_create_lock():
    test = create_lock(user_id="fake", event_date="2019-01")
    assert isinstance(test.get('event_date'), str)


def test_create_lock_faulty_date():
    test = create_lock(user_id="fake", event_date="invalid date string")
    assert test is not True
