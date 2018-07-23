### Instructions

Simple flask app that runs a /slash command
for generating timereport deviations

Create a .env file with TOKEN information for your slack app

```
# slack token variables
SLACK_BOT_TOKEN="xxxxxxx"
SLACK_VERIFICATION_TOKEN="xxxxxx"
# flask listen port
LISTEN_PORT="5000"
# mongodb environment variables
MONGO_HOST="hostname.example.com"
MONGO_PORT="27017"
MONGO_USERNAME="dbuser"
MONGO_PASSWORD="dbpassword"
MONGO_DBNAME="dbname"
```

```
# information

this particular setup runs on AWS lambda using api Gateway.

Deployed through zappa.

pip install zappa
```
