import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)

def delete_event(url, date):
    """
    Delete event for user

    URL: URL to backend API
    date: Date to delete as a string (2019-01-01)
    :return:
    """
    params = {'date': date}
    res = requests.delete(url=url, params=params)
    return res