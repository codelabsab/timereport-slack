import requests
import logging


log = logging.getLogger(__name__)

#####################################################
#        implementation of timereport-api v2        #
#####################################################


def create_event(url: str, event: dict) -> requests.models.Response:
    """Create event

    :param url: str: URL to backend API v2
    :param event: dict: event
    :return: requests.models.Response
    """
    url = f"{url}/events"
    headers = {"Content-Type": "application/json"}
    log.debug(f"url: {url} - headers: {headers}")
    response = requests.post(url=url, json=event, headers=headers)
    return response


def read_event(url: str, user_id: str, date: str) -> requests.models.Response:
    """Get existing timereport for a user

    :param url: str: URL to backend API v2
    :param user_id: str: a user id
    :param date: str: Valid formats: "2019-01", "2019-01-01", "2019-01-02:2019-01-03"
    :return: requests.models.Response
    """
    url = f"{url}/users/{user_id}/events/{date}"
    headers = {"Content-Type": "application/json"}
    log.debug(f"url: {url} - user_id: {user_id} - headers: {headers}")
    response = requests.get(url=url, headers=headers)
    return response


def delete_event(url: str, user_id: str, date: str) -> requests.models.Response:
    """Delete event for user

    :param url: URL to backend API v2
    :param user_id: str: user_id
    :param date: Date to delete as a string (2019-01-01)
    :return: requests.models.Response
    """
    log.debug(f"url: {url} - user_id: {user_id} - date: {date}")
    response = requests.delete(url=f"{url}/users/{user_id}/events/{date}")
    return response


def create_lock(url: str, user_id: str, date: str) -> requests.models.Response:
    """Lock month for user

    :param url: str: URL to backend API v2
    :param user_id: str: user_id
    :param date: str: date in "YYYY-mm"
    :type sent: dict: {"user_id":"foo01","event_date":"2019-02"}
    :return: requests.models.Response
    """
    url = f"{url}/locks"
    headers = {"Content-Type": "application/json"}
    data = {"user_id": user_id, "event_date": date}
    log.debug(f"url: {url} - data: {data} - headers: {headers}")
    response = requests.post(url=url, data=data, headers=headers)
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
    headers = {"Content-Type": "application/json"}
    log.debug(f"url: {url} - user_id: {user_id} - headers: {headers}")
    response = requests.get(url=url, headers=headers)
    return response
