import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)

def create_event(url, data):
    """
    Uses new python chalice backend
    only returns back at this point, no DB connection

    :method: POST
    :url: '/event'
    :return: current_request.raw_body.decode() (same data you send in)
    """
    headers={'Content-Type': 'application/json'}
    res = requests.post(url=url, json=data, headers=headers)
    if res.status_code == 200:
        return True
    else:
        return False
