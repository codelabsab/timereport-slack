def slack_responder(url, msg):
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=url, data={"text": f"{msg}"}, headers=headers)
    if res.status_code == 200:
        return True
    else:
        return False


def slack_payload_extractor(req):
    '''
    Returns a dict containing the pure slack payload. Removes apigw metadata.
    '''
    d = {}
    for param in req['body'].split("&"):
        key, value = param.split("=")
        d[key] = value
    return d


def verify_token(token):
    if token == os.environ['SLACK_TOKEN']:
        return True
    else:
        return False
