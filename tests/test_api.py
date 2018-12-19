import timereport.api as api

from tests.test_data import data
import os

def main():
    # set os.environ SLACK_TOKEN
    os.environ["SLACK_TOKEN"] = api.config['SLACK_TOKEN']
    api.lambda_handler(data, None)


if __name__ == '__main__':
    main()

