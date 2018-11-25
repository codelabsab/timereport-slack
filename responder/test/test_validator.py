import unittest

import responder.validator as validator

class Validate(unittest.TestCase):

    def test_type(self):
        self.assertTrue(validator.validate_type('timereport vab 2018-09-11:2018-09-12 8'))
        self.assertFalse(validator.validate_type('timereport wrong 2018-09-11:2018-09-12 8'))

    def test_date_start(self):
        self.assertTrue(validator.validate_date_start('timereport vab 2018-09-11:2018-09-12 8'))
        self.assertTrue(validator.validate_date_start('timereport vab 2018-09-11 2018-09-12 8'))
        self.assertTrue(validator.validate_date_start('timereport vab today 8'))
        self.assertTrue(validator.validate_date_start('timereport vab today'))

        self.assertFalse(validator.validate_date_start('timereport vab 2018-09-11-2018-09-12 8'))
        self.assertFalse(validator.validate_date_start('timereport vab 20180911-20180912 8'))
        self.assertFalse(validator.validate_date_start('timereport vab 2018/09/11:2018/09/12 8'))
        self.assertFalse(validator.validate_date_start('timereport vab 2099-111-01:2099-111-12 8'))

    def test_date_end(self):
        self.assertTrue(validator.validate_date_end('timereport vab 2018-09-11:2018-09-12 8'))
        # Should be True since date_end is optional and can be empty / None
        self.assertTrue(validator.validate_date_end('timereport vab 2018-09-11 8'))
        self.assertTrue(validator.validate_date_end('timereport vab 2018-09-11'))
        # no : provided so <date_end> becomes is None
        self.assertTrue(validator.validate_date_end('timereport vab today 8'))
        self.assertTrue(validator.validate_date_end('timereport vab 2018-09-11 today 8'))
        self.assertTrue(validator.validate_date_end('timereport vab 2018-09-11-2018-09-12 8'))
        self.assertTrue(validator.validate_date_end('timereport vab 8'))
        self.assertFalse(validator.validate_date_end('timereport vab 2018-09-11:apa 8'))



    def test_hour(self):
        self.assertTrue(validator.validate_hour('timereport vab 2018-09-11:2018-09-12 8'))
        self.assertTrue(validator.validate_hour('timereport vab 2018-09-11 8'))
        self.assertTrue(validator.validate_hour('timereport vab 2018-09-11'))
        # even if we leave <hour> empty it will be ok
        self.assertTrue(validator.validate_hour('timereport vab'))
        # Since we only test/validate the hour and it is correct
        self.assertTrue(validator.validate_hour('timereport vab 2018-09-11-2018-09-12 8'))

        self.assertFalse(validator.validate_hour('timereport vab today 0'))
        self.assertFalse(validator.validate_hour('timereport vab 2018-09-11 today 15'))

    def test_all(self):
        self.assertTrue(all(True *validator.validate_all('timereport vab 2018-09-11:2018-09-12 8')))
        self.assertTrue(all(True *validator.validate_all('timereport vab 2018-09-11')))
        self.assertFalse(any(False *validator.validate_all('timereport vab 2018-09-11 today 15')))
        self.assertFalse(any(False *validator.validate_all('timereport vab 2018-09-11-2018-09-12 8')))


if __name__ == '__main__':
    unittest.main()