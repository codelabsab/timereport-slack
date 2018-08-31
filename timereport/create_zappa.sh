#!/bin/bash
# create zappa_settings.json
# from env variables inside travis
cat << EOF > zappa_settings.json
{
    "timereport": {
        "app_function": "timereport.app",
        "profile_name": "default",
        "project_name": "slack_timereport",
        "runtime": "python3.6",
        "s3_bucket": "timereport.codelabs.se",
        "aws_region": "us-east-1",
        "aws_environment_variables": {
            "LISTEN_PORT" : $aws_environment_variables['LISTEN_PORT'],
            "SLACK_BOT_TOKEN" : $aws_environment_variables['SLACK_BOT_TOKEN'],
            "SLACK_APP_ID" : "",
            "SLACK_SECRET" : "",
            "SLACK_CLIENT_ID" : "",
            "SLACK_VERIFICATION_TOKEN" : "",
            "SLACK_OAUTH_ACCESS_TOKEN" :"",
            "SLACK_BOT_USER_OAUTH_ACCESS_TOKEN" :"",
            "MONGO_HOST" :"",
            "MONGO_PORT" :"47451",
            "MONGO_USERNAME" :"",
            "MONGO_PASSWORD" :"",
            "MONGO_DBNAME" : "",
            "REDIS_DB" : "",
            "REDIS_PORT" : "12772",
            "REDIS_PASSWORD" : "",
       }
    }
}
