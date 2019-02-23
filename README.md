# Timereport nextgen

## Architecture
* AWS API Gateway
* AWS Lambda

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
### test coverage
If you want to include test coverage:
```
pytest --cov=timereport 
```
### Packaing secrets for chalice to travis-ci
```
$ tar cvf chalice_secrets.tar timereport/.chalice/{config.json,deployed} timereport/chalicelib/config.json
a timereport/.chalice/config.json
a timereport/.chalice/deployed
a timereport/.chalice/deployed/dev.json
a timereport/chalicelib/config.json

$ travis encrypt-file chalice_secrets.tar --add
encrypting chalice_secrets.tar for codelabsab/timereport
storing result as chalice_secrets.tar.enc
storing secure env variables for decryption

Make sure to add chalice_secrets.tar.enc to the git repository.
Make sure not to add chalice_secrets.tar to the git repository.
Commit all changes to your .travis.yml.

$ git add chalice_secrets.tar.enc .travis.yml

```

### to deploy from local environment

```
#  Setup awscli with your access_key_id and secret_access_key
#  Download chalice_secrets.tar from s3

$ aws s3 cp s3://timereport.codelabs.se/chalice_secrets.tar .

# extract contents and replace the files in your timereport directory with these secret files
# they should never be pushed to github
# follow instructions above to package for chalice and travis-ci

```
