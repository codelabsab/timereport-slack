from timereport.validators import validate_regex


def test_validateRegex_empty():
    test = validate_regex('no', 'match')
    assert test == 'empty'


