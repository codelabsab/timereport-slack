from timereport.validators import validateRegex


def test_validateRegex_empty():
    test = validateRegex('no', 'match')
    assert test == 'empty'


