# Timereport slack

## Architecture
* AWS API Gateway
* AWS Lambda

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
### Packaging secrets for chalice to travis-ci
Download current secrets and extract

```
$ aws s3 cp s3://timereport.codelabs.se/chalice_secrets.tar .
$ tar xvf chalice_secrets.tar
```

If you're making changes, package and upload updated secrets

```
$ tar cvf chalice_secrets.tar .chalice/{config.json,deployed}
a .chalice/config.json
a .chalice/deployed
a .chalice/deployed/dev.json

$ aws s3 cp chalice_secrets.tar s3://timereport.codelabs.se/chalice_secrets.tar
```


### Deploys

Deploys to dev are done automatically on pushes to any branch, this allows easy testing with `/timereport-dev` command in slack.

Deploys to production are done automatically on tagged releases on the master branch.


### to deploy from local environment

Setup awscli with your access_key_id and secret_access_key
Download chalice_secrets.tar from s3

Copy secrets:
```
$ aws s3 cp s3://timereport.codelabs.se/chalice_secrets.tar .
```

extract contents and replace the files in your timereport directory with these secret files
they should never be pushed to github.

Deploy to dev:
```
chalice deploy --stage dev
```

### Dependencies

* `test-requirements.txt`: Packages necessary to run unit tests.
* `requirements.txt`: Packages that chalice will bundle with the lambda
