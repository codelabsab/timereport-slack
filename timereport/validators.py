import datetime
import re


def validateDate(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date, should be YYYY-MM-DD")


def validateRegex(regex, text):
    result = [i for i in re.finditer(regex, text) if i]
    if result:
        for match in result:
            return match.group(1)
    else:
        return ("empty")