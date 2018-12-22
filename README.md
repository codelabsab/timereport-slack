# Timereport nextgen

## Architecture
* AWS API Gateway
* AWS Lambda
* mongodb

## Dev
### Install dependencies
__Install dev packages__

with `pipenv`:
```
pipenv shell
pipenv install --dev
```

If you don't have `pipenv`:
```
pip install -r requirements.txt
pip install -r dev-requirements.txt
```
### Update dependencies
To generate new `requirements.txt`:
```
pipenv lock --requirements > requirements.txt
```
And for dev packages:
```
pipenv lock --requirements --dev > dev-requirements.txt
```
### Run unit tests
Go to root of project.
Then simply run `pytest`:
```
pytest
```

# added python-backend to test out with chalice
