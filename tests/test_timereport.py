from timereport import api
import json
from . import test_data


def test_foo():
    fake_event = json.loads(test_data.d)
    assert api.lambda_handler(fake_event, context=None)
