# Timereport nextgen

## Architecture
* AWS API Gateway
* AWS Lambda

##### File structure
```
.
├── Readme.md
├── __init__.py
├── __pycache__
│   ├── __init__.cpython-36.pyc
│   ├── api.cpython-36.pyc
│   └── app.cpython-36.pyc
├── app.py
├── chalicelib
│   ├── lib
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-36.pyc
│   │   │   ├── add.cpython-36.pyc
│   │   │   ├── factory.cpython-36.pyc
│   │   │   ├── helpers.cpython-36.pyc
│   │   │   ├── list.cpython-36.pyc
│   │   │   └── slack.cpython-36.pyc
│   │   ├── add.py
│   │   ├── factory.py
│   │   ├── helpers.py
│   │   ├── list.py
│   │   └── slack.py
│   └── model
│       ├── __init__.py
│       ├── __pycache__
│       │   ├── __init__.cpython-36.pyc
│       │   └── event.cpython-36.pyc
│       └── event.py
├── config.json
├── data.txt
└── requirements.txt

6 directories, 25 files
```
###### pre-req
- install requirements.txt
- change config.json to use correct endpoints
- or set os.environ for
```
SLACK_TOKEN
python_backend_url
backend_url
```
###### chalice

- To run this locally just pip install requirements and run
```
chalice local
```
- To test with data just run
```
./curl_localhost.sh
```
