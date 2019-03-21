import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)

def get_user_by_id(url, user_id):
    """
    List all posts for user

    :url: The URL to the API
    :user_id: The user_id
    :return: response object
    """
    api_url = f"{url}/user/{user_id}"
    response = requests.get(url=api_url)
    if response.status_code == 200:
        return response.text
    else:
        log.debug(f"Got response code {response.status_code} for user ID {user_id}")
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
