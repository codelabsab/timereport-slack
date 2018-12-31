import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)


def create_event(url, data):
    """
    Post data to backend to create event
    :param url:  URL to backend
    :param data: The data to post
    :return: A boolean
    """
    """
    Uses new python chalice backend
    if endpoint is correctly configured
    it will insert data into table 'event'

    :url: '/event'
    :return: boolean
    """
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=url, data=data, headers=headers)
    log.debug(f'Response code is: {res.status_code}')
    log.debug(f'Url is: {res.url}')
    log.debug(f'Response text: {res.text}')
    if res.status_code == 200:
        return True
    else:
        return False


def post_to_backend(url, data, auth_token):
    params = {'access_token': auth_token}
    res = requests.post(url=url, data=data, params=params)
    log.debug(f'Response code is: {res.status_code}')
    log.debug(f'Url is: {res.url}')
    log.debug(f'Response is: {res.text}')
    if res.status_code == 200:
        return True
    else:
        return False
