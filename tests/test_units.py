from timereport.validators import validateDate, validateRegex
import pytest


def test_invalid_date():
    with pytest.raises(ValueError):
        assert validateDate('fake format')


def test_validateRegex_empty():
    test = validateRegex('no', 'match')
    assert test == 'empty'


