### Instructions

Simple flask app that tests the /slash command

Create a .env file with TOKEN information for your slack app

```
SLACK_BOT_TOKEN="xxxxxxx"
SLACK_VERIFICATION_TOKEN="xxxxxx"
```

edit ```prestart.sh``` to add new python modules. 

Currently installing ```slackclient, python-dotenv ```

run.sh will start a flask app inside docker using the tiangolo/uswgi-nginx image

```
docker run -d --name timereport -p 5000:5000 -v $(pwd)/.env:/app/.env -v $(pwd)/main.py:/app/main.py -v $(pwd)/prestart.sh:/app/prestart.sh tiangolo/uwsgi-nginx                       python2.7

# or 

./run.sh


```

