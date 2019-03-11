from chalicelib.action import Action

def test_action_init():
    fake_payload = dict(text=['fake', 'test'])
    fake_config = dict(slack_token='fake token')
    test = Action(fake_payload, fake_config)
    assert isinstance(test, Action)