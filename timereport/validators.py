import re


def validate_regex(regex, text):
    result = [i for i in re.finditer(regex, text) if i]
    if result:
        for match in result:
            return match.group(1)
    else:
        return "empty"
