import hmac
import hashlib


def verify_token(headers, body, secret):
    """
    https://api.slack.com/docs/verifying-requests-from-slack

    1. Grab timestamp and slack signature from headers.
    2. Concat and create a signature with timestamp + body
    3. Hash the signature together with your signing_secret token from slack settings
    4. Compare digest to slack signature from header
    """
    timestamp = headers['X-Slack-Request-Timestamp']
    slack_signature = headers['X-Slack-Signature']

    basestring = f'v0:{timestamp}:{body}'
    sig = f'v0={hmac.new(bytes(secret, "utf-8"), bytes(basestring, "utf-8"), hashlib.sha256).hexdigest()}'

    if hmac.compare_digest(sig, slack_signature):
        return True
    else:
        return False
