import timereport.api as api

import tests.test_data as test_data
import os

def test_factory(event):
    # set os.environ SLACK_TOKEN
    os.environ["SLACK_TOKEN"] = api.config['SLACK_TOKEN']
    api.lambda_handler(event, None)




# run test_data.add
test_factory(test_data.add)

#run test_data.list
test_factory(test_data.list)