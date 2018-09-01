from timereport.validators import validate_regex
import timereport.config as config
import pytest

def test_validate_regex_empty():
    test = validate_regex('no', 'match')
    assert test == 'empty'

def test_validate_regex():
    test_text = "vab 2018-01-01:2018-01-02 4 fake.fakeson"
    # type_id
    assert validate_regex(config.type_regex, test_text) == 'vab'
    # date_start
    assert validate_regex(config.date_regex_start, test_text) == '2018-01-01'
    # date_end
    assert validate_regex(config.date_regex_end, test_text) == '2018-01-02'
    # hours
    assert validate_regex(config.hour_regex, test_text) == '4'
    # user_name
    assert validate_regex(config.validate_user_name('vab', '2018-01-01', '2018-01-02' ,'4'), test_text) == 'fake.fakeson'

# TODO: Is this really expected behavior of the function?
# When it matches but you don't send in a "group" it will result in an IndexError
def test_validate_regex_faulty():
    with pytest.raises(IndexError):
        assert validate_regex('fake', 'fake data') == 'fail'
