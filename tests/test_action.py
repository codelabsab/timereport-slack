import pytest
from mockito import when, mock, unstub
import botocore.vendored.requests.api as requests

@pytest.fixture
def action():
    fake_payload = dict(
        text=['fake action', 'test'],
        response_url=['http://fakeurl.nowhere'],
        user_id=['fake user']
    )
    fake_config = dict(slack_token='fake token')
    from chalicelib.action import Action
    return Action(fake_payload, fake_config)

def test_perform_unsupported_action(action):
    when(requests).post(
        url=action.response_url, json={'text': 'Unsupported action: fake'}, headers={'Content-Type': 'application/json'}
    ).thenReturn(mock({'status_code': 200}))
    assert action.perform_action() == ''