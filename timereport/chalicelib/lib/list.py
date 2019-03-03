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
    if res.status_code == 200:
        log.debug(f'{res.text}')
        yield res.text
    else:
        return False


def get_between_date(url, start_date, end_date):
    """
    URL :
    /user/<userid>?startDate=<start_date>&endDate=<end_date>
    /user/<user_id>?&startDate=2018-10-05&endDate=2018-12-20

    :param url:
    :param start_date
    :param end_date: endDate
    :return:
    """
    params = {'startDate': start_date, 'endDate': end_date}
    res = requests.get(url=url, params=params)
    if res.status_code == 200:
        yield res.text
    else:
        return False, res.status_code

def get_total_workdays(year, month):
    """
    URL: api.codelabs.se/year-month.json
    :param year:
    :param month:
    :return:

    {"status":"OK","meddelande":"","fran":"2019-02-01","till":"2019-02-28","antal_dagar":28,"antal_vardagar":20,"antal_arbetsdagar":20,"antal_helgdagar":0,"helgdagar":[]}

    """
    url = f'http://api.codelabs.se/{year}-{month}.json'
    res = requests.get(url=url)
    if res.status_code == 200:
        return res.text