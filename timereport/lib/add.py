import botocore.vendored.requests.api as requests


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
