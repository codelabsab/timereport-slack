import logging
from typing import Any, Dict

import requests

from chalicelib.lib.helpers import month_range, parse_date

log = logging.getLogger(__name__)


def get_period_data(date_str: str) -> Dict[str, Any]:
    """
    Get information about the period

    :date_str: A string contaning date. Valid formats: "2019-01", "2019-01-01", "2019-01-02:2019-01-03"
    """

    dates = parse_date(date_str, format_str="%Y-%m")
    if dates["from"] is None or dates["to"] is None:
        dates = parse_date(date_str, format_str="%Y-%m-%d")

    if dates["from"] is None or dates["to"] is None:
        return False

    total_workdays = 0
    holidays = []
    for dt in month_range(dates["from"], dates["to"]):
        month_str = f"{dt.year}-{dt.month:02}"
        api_url = f"http://api.codelabs.se/{month_str}.json"

        response = requests.get(url=api_url, timeout=1)
        if response.status_code == 200:
            data = response.json()
            total_workdays += data["antal_arbetsdagar"]
            holidays += data["helgdagar"]
        else:
            log.debug(f"Got response code {response.status_code} for month {month_str}")

    return dict(total_workdays=total_workdays, holidays=holidays)
