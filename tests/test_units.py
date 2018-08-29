from timereport.validators import validateDate, validateRegex


def test_validateRegex_empty():
    test = validateRegex('no', 'match')
    assert test == 'empty'


