import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)

def delete_event(url, user_id, date):
    """
    URL :
    /event/<user_id>?date=<start_date>
    /event/<user_id>?&date=2018-10-05

    :param url:
    :param user_id
    :param start_date
    :return:
    """
    url = f'{url}/{user_id}'
    params = {'date': date}
    res = requests.delete(url=url, params=params)
    if res.status_code == 200:
        yield res.text
    else:
        return False, res.status_code
