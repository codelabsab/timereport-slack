import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from chalicelib.lib.slack import Slack

logger = logging.getLogger()


def last_month() -> str:
    now = datetime.now()
    month = now.month - 1
    year = now.year

    if month == 0:
        month = 12
        year -= 1

    return f"{year}-{month:02}"


def remind_users(
    slack: Slack, backend_url: str, only_for_user_ids: Optional[List[str]] = None
) -> List[str]:
    api_url = f"{backend_url}/users"
    res = requests.get(url=api_url)
    if res.status_code != 200:
        logger.error(f"Failed to load users: {res.text}")
        return

    month = last_month()

    reminded_users = []

    for user_id, name in json.loads(res.text).items():
        if only_for_user_ids and user_id not in only_for_user_ids:
            continue
        lock_url = f"{backend_url}/users/{user_id}/locks"
        lock_res = requests.get(url=lock_url)
        if res.status_code != 200:
            logger.error(f"Failed to load user locks {user_id}: {res.text}")
            continue

        locked = False
        for lock in json.loads(lock_res.text):
            if lock.get("event_date") == month:
                locked = True

        if not locked:
            slack_res = slack.post_message(
                channel=user_id,
                message=f":unlock: You have not locked {month}",
                as_user=False,
            )
            if slack_res.status_code != 200:
                logger.error(f"Failed to notify slack: {slack_res.text}")
                continue

            reminded_users.append(user_id)

    return reminded_users
