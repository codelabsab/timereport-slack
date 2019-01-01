import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)

def create_event(url, data):
    """
    Uses new python chalice backend
    only returns back at this point, no DB connection

    :method: POST
    :url: '/timereport/event'
    :return: current_request.raw_body.decode() (same data you send in)
    """
    headers={'Content-Type': 'application/json'}
    # these log.debug statements will be removed post-development
    log.debug(f'data is: {data}')
    log.debug(f'url is: {url}')
    log.debug(f'headers are: {headers}')
    res = requests.post(url=url, json=data, headers=headers)
    log.debug(f'{"="*10}')
    log.debug(f'python backend')
    log.debug(f'Response code is: {res.status_code}')
    log.debug(f'Url is: {res.url}')
    log.debug(f'{res.text}')
    log.debug(f'{"="*10}')
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
