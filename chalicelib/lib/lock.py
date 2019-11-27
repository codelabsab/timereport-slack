import requests
import logging

log = logging.getLogger(__name__)


def lock_event(url, event):
    """
    Send lock event

    URL: URL to backend API
    event: The lock event document
    :return:
    """
    headers = {"Content-Type": "application/json"}
    api_url = f"{url}/lock"
    response = requests.post(url=api_url, data=event, headers=headers)
    return response
