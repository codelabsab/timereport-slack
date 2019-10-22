import os
from mockito import when, mock, unstub
from .test_data import fake_request_body
import requests
from chalicelib.lib.slack import (
    slack_payload_extractor, verify_token,
    submit_message_menu, delete_message_menu,
    slack_client_responder, slack_responder, Slack
)



def test_slack_payload_extractor_command():
    fake_data = slack_payload_extractor('command=bar&text=fake+text')
    assert isinstance(fake_data, dict)
    assert fake_data.get('command') == ['bar']
    assert fake_data.get('text') == ['fake text']


def test_slack_payload_extractor_payload():
    fake_data = slack_payload_extractor(
        "payload=%7B%0D%0A+++%22fake%22%3A+%22fake+data%22%0D%0A%7D"
    )
    assert isinstance(fake_data, dict)
    assert fake_data.get('fake') == 'fake data'


def test_signing_secret():
    fake_request_headers = {'X-Slack-Request-Timestamp': '1531420618',
                            'X-Slack-Signature': 'v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503'
                            }
    assert verify_token(fake_request_headers, fake_request_body, 'faultyfaketoken') is not True
    fake_test_token = '8f742231b10e8888abcd99yyyzzz85a5'
    assert verify_token(fake_request_headers, fake_request_body, fake_test_token) is True


def test_slack_client_responder():
    fake_url = 'http://fake.com'
    fake_data = {'channel': 'fake', 'text': 'From timereport', 'attachments': 'fake'}
    fake_headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer fake'}
    when(requests).post(
        url=fake_url, json=fake_data, headers=fake_headers
    ).thenReturn(mock({'status_code': 200, 'text': '{"ok": "true", "message_ts": "xxxxx"}'}))

    test_result = slack_client_responder(
        token='fake',
        user_id='fake',
        attachment='fake',
        url=fake_url,
    )

    assert test_result.status_code == 200
    unstub()


def test_slack_client_responder_failure():
    fake_url = 'http://fake_slack_url.com'
    fake_data = {'channel': 'fake', 'text': 'From timereport', 'attachments': 'fake'}
    fake_headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer fake'}
    when(requests).post(
        url=fake_url, json=fake_data, headers=fake_headers
    ).thenReturn(mock({'status_code': 500}))

    test_result = slack_client_responder(
        token='fake',
        user_id='fake',
        attachment='fake',
        url=fake_url,
    )
    assert test_result.status_code != 200
    unstub()


def test_slack_responder():
    when(requests).post(
        url='fake', json={'text': 'fake message'}, headers={'Content-Type': 'application/json'}
    ).thenReturn(mock({'status_code': 200}))
    assert slack_responder(url='fake', msg='fake message') == 200


def test_submit_menu():
    test_result = submit_message_menu(
        user_name='fake user',
        reason='fake reason',
        date_start='2018-01-01',
        date_end='2018-02-01',
        hours='8',
    )

    assert isinstance(test_result, list)
    test_result_dict = test_result.pop()

    assert isinstance(test_result_dict, dict)
    assert test_result_dict.get('fields')


def test_delete_menu():
    test_result = delete_message_menu(
        user_name='fake user',
        date='2018-01-01',
    )

    assert isinstance(test_result, list)
    test_result_dict = test_result.pop()

    assert isinstance(test_result_dict, dict)
    assert test_result_dict.get('fields')


def test_slack_class():
    test = Slack(slack_token="fake_token")
    assert test.slack_token
    assert test.client