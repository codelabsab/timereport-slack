import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)


def post_event(url, data):
    """
    Add event

    url: URL to backend API
    data: A dict with the event to add
    
    :return: requests response object
    """
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=url, json=data, headers=headers)
    return res
