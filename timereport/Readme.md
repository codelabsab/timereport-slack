# Timereport nextgen

## Architecture
* AWS API Gateway
* AWS Lambda

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
cd timereport
chalice local
```
- To test with data just run
```
./curl_localhost.sh $(chalice url)
```
