import logging
from datetime import date
from chalicelib.lib.api import read_event

import requests

log = logging.getLogger(__name__)


def get_list_data(url, user_id, date_str):
    """
    Get existing timereport for a user

    :url: The URL to the backend API
    :user_id: The users user ID
    :date_str: A string contaning date. Valid formats: "2019-01", "2019-01-01", "2019-01-02:2019-01-03" and ""
    """
    try:
        start_date, end_date = date_str.split(":")
    except ValueError as error:
        log.debug(f"Failed to split: {date_str}")
        log.debug(f"{error}")

        if len(date_str.split("-")) == 2:
            start_date = f"{date_str}-01"
            end_date = f"{date_str}-31"
        else:
            start_date, end_date = date_str, date_str

    except Exception as error:
        log.debug(f"Unexpected exception. Error was: {error}", exc_info=True)
        return False

    response = read_event(
        url=url, user_id=user_id, date={"from": start_date, "to": end_date}
    )
    if response.status_code == 200:
        return response.text
    else:
        log.debug(f"Got response code {response.status_code} for user ID {user_id}")
        return False
