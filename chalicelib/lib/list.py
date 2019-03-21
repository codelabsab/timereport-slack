import botocore.vendored.requests.api as requests
import logging

log = logging.getLogger(__name__)


def get_list_data(url, user_id, date_str=None):
    """
    Get existing timereport for a user

    :url: The URL to the backend API
    :user_id: The users user ID
    :date_str: A string contaning date. Valid formats: "2019-01-01", "2019-01-02:2019-01-03"
    """
    api_url = f"{url}/user/{user_id}"
    date = None if date_str == "all" else True
    if date:
        try:
            start_date, end_date = date_str.split(":")
        except ValueError as error:
            log.debug(f"Failed to split: {date_str}")
            log.debug(f"Error was: {error}", exc_info=True)
            start_date, end_date = date_str, date_str

        date_str = {"startDate": start_date, "endDate": end_date}

    response = requests.get(url=api_url, params=date_str)
    if response.status_code == 200:
        return response.text
    else:
        log.debug(f"Got response code {response.status_code} for user ID {user_id}")
        return False
