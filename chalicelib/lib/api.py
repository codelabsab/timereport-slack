import botocore.vendored.requests.api as requests
import logging
import os

log = logging.getLogger(__name__)

####################################################
#                                                  #
#        implementation of timereport-api v2       #
#                                                  #
####################################################


url = os.getenv('backend_url', 'localhost:8000')


def create(data):
    """
    Create event

    url: URL to backend API
    data: A dict with the event to add
    
    :return: requests response object
    """
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=url, json=data, headers=headers)
    return res


def delete(user_id, date):
    """
    Delete event for user

    URL: URL to backend API
    date: Date to delete as a string (2019-01-01)
    :return:
    """
    # TODO:
    #  Implement security: api should demand token in header
    #  headers = {f"token: {secret_token}"}
    res = requests.delete(url=f"{url}/users/{user_id}/events/{date}")
    return res


def read(url, user_id, date_str):
    """
    Get existing timereport for a user

    :url: The URL to the backend API
    :user_id: The users user ID
    :date_str: A string contaning date. Valid formats: "2019-01", "2019-01-01", "2019-01-02:2019-01-03"
    """
    api_url = f"{url}/event/users/{user_id}"
    try:
        start_date, end_date = date_str.split(":")
    except ValueError as error:
        log.debug(f"Failed to split: {date_str}")

        if len(date_str.split("-")) == 2:
            start_date = f"{date_str}-01"
            end_date = f"{date_str}-31"
        else:
            start_date, end_date = date_str, date_str

    except Exception as error:
        log.debug(f"Unexpected exception. Error was: {error}", exc_info=True)
        return False

    date_str = {"startDate": start_date, "endDate": end_date}

    response = requests.get(url=api_url, params=date_str)
    if response.status_code == 200:
        return response.text
    else:
        log.debug(f"Got response code {response.status_code} for user ID {user_id}")
        return False


def lock(url, data):
    """
    Lock month for user

    URL: URL to backend API
    event: The lock event document
    :return:
    """
    headers={'Content-Type': 'application/json'}
    url = f'{url}/locks'
    response = requests.post(url=url, data=data, headers=headers)
    return response