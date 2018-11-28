#####
```
{
    "resource": "/no-wsgi-app",
    "path": "/no-wsgi-app",
    "httpMethod": "POST",
    "headers": {
        "Accept": "application/json,*/*",
        "Accept-Encoding": "gzip,deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "hp2zas87ei.execute-api.us-east-1.amazonaws.com",
        "User-Agent": "Slackbot 1.0 (+https://api.slack.com/robots)",
        "X-Amzn-Trace-Id": "Root=1-5bfe8087-979564f5fd3f790d05438482",
        "X-Forwarded-For": "52.23.209.252",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https",
        "X-Slack-Request-Timestamp": "1543405703",
        "X-Slack-Signature": "v0=380f2d034323ba736ccfba886d83dec1ab0989c32dd2764422a4d07921987ec7"
    },
    "multiValueHeaders": {
        "Accept": [
            "application/json,*/*"
        ],
        "Accept-Encoding": [
            "gzip,deflate"
        ],
        "Content-Type": [
            "application/x-www-form-urlencoded"
        ],
        "Host": [
            "hp2zas87ei.execute-api.us-east-1.amazonaws.com"
        ],
        "User-Agent": [
            "Slackbot 1.0 (+https://api.slack.com/robots)"
        ],
        "X-Amzn-Trace-Id": [
            "Root=1-5bfe8087-979564f5fd3f790d05438482"
        ],
        "X-Forwarded-For": [
            "52.23.209.252"
        ],
        "X-Forwarded-Port": [
            "443"
        ],
        "X-Forwarded-Proto": [
            "https"
        ],
        "X-Slack-Request-Timestamp": [
            "1543405703"
        ],
        "X-Slack-Signature": [
            "v0=380f2d034323ba736ccfba886d83dec1ab0989c32dd2764422a4d07921987ec7"
        ]
    },
    "queryStringParameters": null,
    "multiValueQueryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "requestContext": {
        "resourceId": "a23mft",
        "resourcePath": "/no-wsgi-app",
        "httpMethod": "POST",
        "extendedRequestId": "REkFLEeeIAMF7RQ=",
        "requestTime": "28/Nov/2018:11:48:23 +0000",
        "path": "/default/no-wsgi-app",
        "accountId": "106618949447",
        "protocol": "HTTP/1.1",
        "stage": "default",
        "domainPrefix": "hp2zas87ei",
        "requestTimeEpoch": 1543405703579,
        "requestId": "8290f6fd-f303-11e8-ab94-ef66c989760f",
        "identity": {
            "cognitoIdentityPoolId": null,
            "accountId": null,
            "cognitoIdentityId": null,
            "caller": null,
            "sourceIp": "52.23.209.252",
            "accessKey": null,
            "cognitoAuthenticationType": null,
            "cognitoAuthenticationProvider": null,
            "userArn": null,
            "userAgent": "Slackbot 1.0 (+https://api.slack.com/robots)",
            "user": null
        },
        "domainName": "hp2zas87ei.execute-api.us-east-1.amazonaws.com",
        "apiId": "hp2zas87ei"
    },
    "body": "token=OwjK95k89vMbtbyvhvLZkXNl&team_id=T2FG58LDV&team_domain=codelabsab&channel_id=CA8THJML6&channel_name=development&user_id=U2FGC795G&user_name=kamger&command=%2Fno-wsgi&text=vab+today&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F491076166711%2FbVUlrKZrnElSOBUqn01FoxNf&trigger_id=490225208629.83549292471.860541eab9e9c3c6d7464ea2e979c7a5",
    "isBase64Encoded": false
}

[INFO]    2018-11-28T11:48:23.880Z    82916c0f-f303-11e8-96d7-15e8d92f88e2    Recevied event body is parsed 
{'token': ['OwjK95k89vMbtbyvhvLZkXNl'], 'team_id': ['T2FG58LDV'], 'team_domain': ['codelabsab'], 'channel_id': ['CA8THJML6'], 'channel_name': ['development'], 'user_id': ['U2FGC795G'], 'user_name': ['kamger'], 'command': ['/no-wsgi'], 'text': ['vab today'], 'response_url': ['https://hooks.slack.com/commands/T2FG58LDV/491076166711/bVUlrKZrnElSOBUqn01FoxNf'], 'trigger_id': ['490225208629.83549292471.860541eab9e9c3c6d7464ea2e979c7a5']}
[INFO]    2018-11-28T11:48:23.987Z    82916c0f-f303-11e8-96d7-15e8d92f88e2    Starting new HTTPS connection (1): hooks.slack.com
END RequestId: 82916c0f-f303-11e8-96d7-15e8d92f88e2
REPORT RequestId: 82916c0f-f303-11e8-96d7-15e8d92f88e2    Duration: 312.69 ms    Billed Duration: 400 ms Memory Size: 128 MB    Max Memory Used: 25 MB    
START RequestId: 92d6013b-f303-11e8-af88-773d6f829094 Version: $LATEST
[INFO]    2018-11-28T11:48:50.891Z    92d6013b-f303-11e8-af88-773d6f829094    Received event is dumped in JSON format:
{
    "resource": "/no-wsgi-app",
    "path": "/no-wsgi-app",
    "httpMethod": "POST",
    "headers": {
        "Accept": "application/json,*/*",
        "Accept-Encoding": "gzip,deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "hp2zas87ei.execute-api.us-east-1.amazonaws.com",
        "User-Agent": "Slackbot 1.0 (+https://api.slack.com/robots)",
        "X-Amzn-Trace-Id": "Root=1-5bfe80a2-7a9d5b8c56ab5f46186af95a",
        "X-Forwarded-For": "18.233.66.199",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https",
        "X-Slack-Request-Timestamp": "1543405730",
        "X-Slack-Signature": "v0=9395dd23bfe8eca74ff373c2f3f6b13592549e9ac18b68cdea5983406b1f7b05"
    },
    "multiValueHeaders": {
        "Accept": [
            "application/json,*/*"
        ],
        "Accept-Encoding": [
            "gzip,deflate"
        ],
        "Content-Type": [
            "application/x-www-form-urlencoded"
        ],
        "Host": [
            "hp2zas87ei.execute-api.us-east-1.amazonaws.com"
        ],
        "User-Agent": [
            "Slackbot 1.0 (+https://api.slack.com/robots)"
        ],
        "X-Amzn-Trace-Id": [
            "Root=1-5bfe80a2-7a9d5b8c56ab5f46186af95a"
        ],
        "X-Forwarded-For": [
            "18.233.66.199"
        ],
        "X-Forwarded-Port": [
            "443"
        ],
        "X-Forwarded-Proto": [
            "https"
        ],
        "X-Slack-Request-Timestamp": [
            "1543405730"
        ],
        "X-Slack-Signature": [
            "v0=9395dd23bfe8eca74ff373c2f3f6b13592549e9ac18b68cdea5983406b1f7b05"
        ]
    },
    "queryStringParameters": null,
    "multiValueQueryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "requestContext": {
        "resourceId": "a23mft",
        "resourcePath": "/no-wsgi-app",
        "httpMethod": "POST",
        "extendedRequestId": "REkJcHWCoAMFm0Q=",
        "requestTime": "28/Nov/2018:11:48:50 +0000",
        "path": "/default/no-wsgi-app",
        "accountId": "106618949447",
        "protocol": "HTTP/1.1",
        "stage": "default",
        "domainPrefix": "hp2zas87ei",
        "requestTimeEpoch": 1543405730872,
        "requestId": "92d58b9c-f303-11e8-9b86-f19fb435e177",
        "identity": {
            "cognitoIdentityPoolId": null,
            "accountId": null,
            "cognitoIdentityId": null,
            "caller": null,
            "sourceIp": "18.233.66.199",
            "accessKey": null,
            "cognitoAuthenticationType": null,
            "cognitoAuthenticationProvider": null,
            "userArn": null,
            "userAgent": "Slackbot 1.0 (+https://api.slack.com/robots)",
            "user": null
        },
        "domainName": "something.execute-api.us-east-1.amazonaws.com",
        "apiId": "hp2zas87ei"
    },
    "body": "token=aaabbbbbcccczzztokenxxxxxx&team_id=T2FG58LDV&team_domain=codelabsab&channel_id=CA8THJML6&channel_name=development&user_id=U2FGC795G&user_name=kamger&command=%2Fno-wsgi&text=apa+banan+kokain+kola+fanta+sprite&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F489856937716%2FJUaZIKdO6f73ofdI3M3l6D9F&trigger_id=489288274320.83549292471.8d89a81c398bcbc9dd35addfd54af992",
    "isBase64Encoded": false
}
```
