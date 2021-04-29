# Timereport slack

## Architecture
* AWS API Gateway
* AWS Lambda
* AWS SQS

The project is build with AWS Chalice, allowing us to specify all infrastructure as part of the code. The entrypoint is `app.py` where all external communication is handled. NOTE: SQS queues are created manually using AWS CLI at Travis.

#### Important classes and concepts

* Action - Something that you want to do, for example `add` using the command `/timereport add` in Slack. In this case `Add` is the action and is represented by a class in `chalicelib/action.py`.
* Slack - The public interface of the project is a slack-command `/timereport`
* Command - When someone calls `/timereport` in slack, we get a command that is handled by the `/command` endpoint in `app.py`
* Interactive - Some actions require confirmation, interactive is the confirmation (or rejection) of a confirmation prompt. When someone confirms a command slack issues an interactive reply and is handled by the `/interactive` in `app.py`
* Timereport-api - Another service used to store the worked time, everything stored from this project is stored there. All communication is done over HTTP
* SQS - Amazon provided queue, we're using it to handle tasks in the background. See below for more information


#### Background tasks

Slack requires all calls to endpoints to be replied to in 3 seconds. This makes it hard for us to do all processing of a command. To be able to handle this we have decided to use SQS as a queue. Below follows the flow for the `/command` endpoint but `/interactive` follows an identical flow.

1. User sends the following in slack: `/timereport list 2020-09`
2. We receive a call to our endpoint `/command` with data containing the command and metadata about the user
3. We parse and verify the payload, directly in the endpoint and in the `is_valid` method of the Action
4. If we see any validation errors we reply to Slack and abort the processing, a message will be shown to the user about the error
5. A message is put on the `command queue`
6. We reply to slack that we received the message and will process it, normally nothing is shown to the user in this step
7. The message on the `command queue` is received by the `command_handler` in `app.py`
8. The `Action` class will perform the action, loading data from `timereport-api` and respond to slack

## Dev
### Install dependencies
__Install dev packages__


##### Install pre-commit

MacOS:

```
$ brew install pre-commit
```

Install git-commit hook

##### Pipenv

with `pipenv`:
```
pipenv shell
pipenv install --dev
```

### Run unit tests
Go to root of project.
Then simply run `pytest`:
```
pytest
```
### test coverage
If you want to include test coverage:
```
pytest --cov=chalicelib
```

### Deploys

Deploys to dev are done automatically on pushes to any branch, this allows easy testing with `/timereport-dev` command in slack.

Deploys to production are done automatically on tagged releases on the master branch.


### to deploy from local environment

Setup awscli with your access_key_id and secret_access_key

#### Configure

To create the config use the script [template-config.py](template-config.py)
It uses the template [config.json.j2](config.json.j2).

The script expects environment variables. See the [dev pipeline](.github/workflows/dev.yml) or look in the script.
they should never be pushed to github.

Run:
```
# python template-config.py
```
You should now have .chalice/config.json with appropriate values

Deploy to dev:
```
chalice deploy --stage dev
```

### Dependencies

* `test-requirements.txt`: Packages necessary to run unit tests.
* `requirements.txt`: Packages that chalice will bundle with the lambda
