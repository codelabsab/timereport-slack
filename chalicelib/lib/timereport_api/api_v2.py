import botocore.vendored.requests.api as requests
import botocore.vendored.requests.models
import logging


log = logging.getLogger(__name__)

#####################################################
#                                                   #
#        implementation of timereport-api v2        #
#                                                   #
#####################################################


def create(url: str, event: dict) -> botocore.vendored.requests.models.Response:
    """Create event

    :param url: str: URL to backend API v2
    :param event: dict: event
    :return: botocore.vendored.requests.models.Response
    """
    headers = {"Content-Type": "application/json"}
    response = requests.post(url=url, json=event, headers=headers)
    return response


def delete(
    url: str, user_id: str, date: str
) -> botocore.vendored.requests.models.Response:
    """Delete event for user

    :param url: URL to backend API v2
    :param user_id: str: user_id
    :param date: Date to delete as a string (2019-01-01)
    :return: botocore.vendored.requests.models.Response
    """
    # TODO:
    #  Implement security: api should demand token in header
    #  headers = {f"token: {secret_token}"}
    response = requests.delete(url=f"{url}/users/{user_id}/events/{date}")
    return response


def read(
    url: str, user_id: str, date: str
) -> botocore.vendored.requests.models.Response:
    """Get existing timereport for a user

    :param url: str: URL to backend API v2
    :param user_id: str: a user id
    :param date: str: Valid formats: "2019-01", "2019-01-01", "2019-01-02:2019-01-03"
    :return: requests.models.Response
    """
    url = f"{url}/users/{user_id}/events/{date}"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url=url, headers=headers)
    return response


def lock(
    url: str, user_id: str, date: str
) -> botocore.vendored.requests.models.Response:
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
    response = requests.post(url=url, data=data, headers=headers)
    return response
