import botocore.vendored.requests.api as requests


def create_event(url, data):
    """
    Uses new python chalice backend
    only returns back at this point, no DB connection

    :method: POST
    :url: '/timereport/event'
    :return: current_request.raw_body.decode() (same data you send in)
    """
    headers={'Content-Type': 'application/json'}
    res = requests.post(url=url, data=data, headers=headers)
    print(f'{"="*10}')
    print(f'python backend')
    print(f'Response code is: {res.status_code}')
    print(f'Url is: {res.url}')
    print(f'{res.text}')
    print(f'{"="*10}')
    if res.status_code == 200:
        return True
    else:
        return False


def post_to_backend(url, data, auth_token):
    params = {'access_token': auth_token}
    res = requests.post(url=url, data=data, params=params)
    print(f'Response code is: {res.status_code}')
    print(f'Url is: {res.url}')
    print(f'Response is: {res.text}')
    if res.status_code == 200:
        return True
    else:
        return False
