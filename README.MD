### Instructions

Simple flask app that runs a /slash command
for generating timereport deviations

Create a .env file with TOKEN information for your slack app or use Zappa
with the following zappa_settings.json file.

deploy with zappa.

```
pip install zappa

zappa deploy timereport

```
# zappa_settings.json
{
    "timereport": {
        "app_function": "timereport.app",
        "profile_name": "default",
        "project_name": "slack_timereport",
        "runtime": "python3.6",
        "s3_bucket": "timereport.s3.bucketname.com",
        "aws_region": "us-east-1",
        "aws_environment_variables": {
            "LISTEN_PORT" : "5000",
            "SLACK_BOT_TOKEN" :"",
            "SLACK_APP_ID" :"",
            "SLACK_SECRET" :"",
            "SLACK_CLIENT_ID" :"",
            "SLACK_VERIFICATION_TOKEN" :"",
            "SLACK_OAUTH_ACCESS_TOKEN" :"",
            "SLACK_BOT_USER_OAUTH_ACCESS_TOKEN" :"",
            "MONGO_HOST" :"mongohostname.com",
            "MONGO_PORT" :"47451",
            "MONGO_USERNAME" :"User",
            "MONGO_PASSWORD" :"Password",
            "MONGO_DBNAME" : "DBname",
            "REDIS_DB" : "redishostname",
            "REDIS_PORT" : "12772",
            "REDIS_PASSWORD" : "Password",
       }
    }
}
```

```
# information

this particular setup runs everything in separate endpoints
on aws lambda.

Deployed through zappa.

- zappa
- flask
- redis
- pandas
- mongodb
- aws lambda
- aws api gateway
- aws s3

you need to set up api.slack.com for your app
with interactive_messaging and correct endpoint urls
as well as slash commands.
```
