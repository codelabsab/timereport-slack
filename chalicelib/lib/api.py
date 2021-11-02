import requests
import logging
import os

log = logging.getLogger(__name__)

#####################################################
#        implementation of timereport-api v2        #
#####################################################

# TODO: This should be provided via app.py as rest of config.
# Maybe convert this to a class to make it easy to setup URL and api key
backend_api_key = os.getenv("backend_api_key", "development")
headers = {"Content-Type": "application/json", "Authorization": backend_api_key}


def create_event(url: str, event: dict) -> requests.models.Response:
    """Create event

    :param url: str: URL to backend API v2
    :param event: dict: event
    :return: requests.models.Response
    """
    url = f"{url}/events"
    response = requests.post(url=url, json=event, headers=headers)
    return response


def read_event(url: str, user_id: str, date: dict) -> requests.models.Response:
    """Get existing timereport for a user

    :param url: str: URL to backend API v2
    :param user_id: str: a user id
    :param date: dict: Valid formats: {"from": "2019-01-01"}, {"from": "2019-01-02", "to": "2019-01-03"}
    :return: requests.models.Response
    """
    if not date.get("to"):
        date["to"] = date["from"]

    url = f"{url}/users/{user_id}/events"
    response = requests.get(url=url, headers=headers, params=date)
    return response


def delete_event(url: str, user_id: str, date: str) -> requests.models.Response:
    """Delete event for user

    :param url: URL to backend API v2
    :param user_id: str: user_id
    :param date: Date to delete as a string (2019-01-01)
    :return: requests.models.Response
    """
    url = f"{url}/users/{user_id}/events/{date}"
    response = requests.delete(url=url, headers=headers)
    return response


def create_lock(url: str, user_id: str, date: str) -> requests.models.Response:
    """Lock month for user

    :param url: str: URL to backend API v2
    :param user_id: str: user_id
    :param date: str: date in "YYYY-mm"
    :return: requests.models.Response
    """
    url = f"{url}/locks"
    data = {"user_id": user_id, "event_date": date}
    log.debug(f"Create lock data is: {data}")
    response = requests.post(url=url, json=data, headers=headers)
    return response


def read_lock(url: str, user_id: str) -> requests.models.Response:
    """
    List locks for user. Response contains a list of all locks for user
    and will need to get parsed on our side.
    :param url: str
    :param user_id: str
    :return: requests.models.Response
    """
    url = f"{url}/users/{user_id}/locks"
    response = requests.get(url=url, headers=headers, timeout=3)
    return response
