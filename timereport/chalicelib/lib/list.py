import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)

def get_user_by_id(url, user_id):
    """
    Uses new python chalice backend
    only returns back at this point, no DB connection

    :method: GET
    :url: /timereport/user/{user_id}
    :return: {'user_id': user_id}
    """
    url = url + '/' + user_id
    res = requests.get(url=url)
    log.debug(f'{"="*10}')
    log.debug(f'python backend')
    log.debug(f'Response code is: {res.status_code}')
    log.debug(f'Url is: {res.url}')
    log.debug(f'{res.text}')
    log.debug(f'{"="*10}')
    if res.status_code == 200:
        yield res.text
    else:
        return False


def get_between_date(url, start_date, auth_token, end_date):
    """
    URL :
    /api/v2/timereport?access_token=<slack_team_id>&startDate=<start_date>&endDate=<end_date>
    /api/v2/timereport?access_token=N2FG58LXY&startDate=2018-10-05&endDate=2018-12-20

    :param url:
    :param data: startDate
    :param auth_token:
    :param end_date: endDate
    :return:
    """
    params = {'access_token': auth_token, 'startDate': start_date, 'endDate': end_date}
    res = requests.get(url=url, params=params)
    log.debug(f'Response code is: {res.status_code}')
    log.debug(f'Url is: {res.url}')
    for resp in res.json():
        log.debug(f'{resp}')
    if res.status_code == 200:
        return True
    else:
        return False
