#!/bin/bash
docker run -d --name timereport -p 5000:5000 -v $(pwd)/.env:/app/.env -v $(pwd)/main.py:/app/main.py -v $(pwd)/prestart.sh:/app/prestart.sh tiangolo/uwsgi-nginx                       python2.7
