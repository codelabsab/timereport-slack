import os
import botocore.vendored.requests.api as requests
from urllib.parse import parse_qs
import logging
import json
import hmac
import hashlib
import base64

log = logging.getLogger(__name__)


def slack_client_responder(token, user_id, attachment, url='https://slack.com/api/chat.postMessage'):
    """
    Sends an direct message to a user.
    https://api.slack.com/methods/chat.postEphemeral

    :param token: slack token
    :param user_id: The user id
    :param attachment: The slack attachment
    :param url: The slack URL
    :return: request response object
    """

    log.debug(f"Will try to post direct message to user {user_id}")
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': f'Bearer {token}'}
    return requests.post(
        url=url,
        json={'channel': user_id, 'text': 'From timereport', 'attachments': attachment},
        headers=headers
    )


def slack_responder(url, msg):
    """
    Sends post to slack_response_url
    :param url: slack response_url
    :param msg:
    :return: boolean
    """
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=url, json={"text": msg}, headers=headers)
    return res.status_code


def slack_payload_extractor(req):
    """
    Extract the body data of the slack request.

    :param req: The request data from slack
    :return: dict

    {
	'type': 'interactive_message',
	'actions': [{
		'name': 'submit',
		'type': 'button',
		'value': 'submit_yes'
	}],
	'callback_id': 'submit',
	'team': {
		'id': 'T2FG58LDV',
		'domain': 'codelabsab'
	},
	'channel': {
		'id': 'CBCMH0YSZ',
		'name': 'timereports'
	},
	'user': {
		'id': 'U2FGC795G',
		'name': 'kamger'
	},
	'action_ts': '1549534734.479730',
	'message_ts': '1549534730.003400',
	'attachment_id': '1',
	'token': 'ZfnrFKdHTDIy3f60ahIw4HO4',
	'is_app_unfurl': False,
	'original_message': {
		'type': 'message',
		'subtype': 'bot_message',
		'text': 'U2FGC795G from slack.py',
		'ts': '1549534730.003400',
		'username': 'timereport-dev',
		'bot_id': 'BEB7VGM28',
		'attachments': [{
			'callback_id': 'submit',
			'fallback': 'Submit these values?',
			'title': 'Submit these values?',
			'footer': 'Code Labs timereport',
			'id': 1,
			'footer_icon': 'https://codelabs.se/favicon.ico',
			'color': '3AA3E3',
			'fields': [{
				'title': 'User',
				'value': 'kamger',
				'short': False
			}, {
				'title': 'Type',
				'value': 'vab',
				'short': False
			}, {
				'title': 'Date start',
				'value': '2018-12-03',
				'short': False
			}, {
				'title': 'Date end',
				'value': '2018-12-03',
				'short': False
			}, {
				'title': 'Hours',
				'value': '2018-12-05',
				'short': False
			}],
			'actions': [{
				'id': '1',
				'name': 'submit',
				'text': 'submit',
				'type': 'button',
				'value': 'submit_yes',
				'style': 'primary'
			}, {
				'id': '2',
				'name': 'no',
				'text': 'No',
				'type': 'button',
				'value': 'submit_no',
				'style': 'danger'
			}]
		}]
	},
	'response_url': 'https://hooks.slack.com/actions/T2FG58LDV/544051725409/hFalBemCS5sOQYWARMTvJVyB',
	'trigger_id': '544051725457.83549292471.e4c1ada0676cb35dc512881689b3b01c'
}
    """
    data = parse_qs(req)

    log.debug(f"data is: {data}")

    if data.get("payload"):
        extracted_data = json.loads(data.get('payload')[0])
        log.info(f'Extracted data: {extracted_data}')
        return extracted_data

    if data.get('command'):
        return data
    else:
        return "failed extracting payload", 200


def verify_token(headers, body, signing_secret):
    """
    https://api.slack.com/docs/verifying-requests-from-slack

    1. Grab timestamp and slack signature from headers.
    2. Concat and create a signature with timestamp + body
    3. Hash the signature together with your signing_secret token from slack settings
    4. Compare digest to slack signature from header
    """
    request_timestamp = headers['X-Slack-Request-Timestamp']
    request_basestring = bytes(f'v0:{request_timestamp}:{body}', 'utf-8')
    slack_signature = headers['X-Slack-Signature']
    signing_secret = bytes(signing_secret, 'utf-8')
    my_sig = f'v0={hmac.new(signing_secret, request_basestring, hashlib.sha256).hexdigest()}'

    # compare to slack-signature
    if hmac.compare_digest(my_sig, slack_signature):
        return True
    else:
        return False

def verify_reasons(valid_reasons, reason):
    if reason in valid_reasons:
        return True
    else:
        return False


def submit_message_menu(user_name, reason, date_start, date_end, hours):
    attachment = [
        {
            "fields": [
                {
                    "title": "User",
                    "value": user_name
                },

                {
                    "title": "Type",
                    "value": reason
                },
                {
                    "title": "Date start",
                    "value": date_start
                },
                {
                    "title": "Date end",
                    "value": date_end
                },

                {
                    "title": "Hours",
                    "value": hours
                }
            ],
            "footer": "Code Labs timereport",
            "footer_icon": "https://codelabs.se/favicon.ico",
            "fallback": "Submit these values to database?",
            "title": "Submit these values to database?",
            "callback_id": "add",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "submit",
                    "text": "submit",
                    "type": "button",
                    "style": "primary",
                    "value": "submit_yes"
                },
                {
                    "name": "no",
                    "text": "No",
                    "type": "button",
                    "style": "danger",
                    "value": "submit_no"
                }
            ]
        }
    ]
    return attachment


def delete_message_menu(user_name, date):
    attachment = [
        {
            "fields": [
                {
                    "title": "User",
                    "value": user_name
                },
                {
                    "title": "Date",
                    "value": date
                }
            ],
            "footer": "Code Labs timereport",
            "footer_icon": "https://codelabs.se/favicon.ico",
            "fallback": "Delete these values from database?",
            "title": "Delete these values from database?",
            "callback_id": "delete",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "submit",
                    "text": "submit",
                    "type": "button",
                    "style": "primary",
                    "value": "submit_yes"
                },
                {
                    "name": "no",
                    "text": "No",
                    "type": "button",
                    "style": "danger",
                    "value": "submit_no"
                }
            ]
        }
    ]
    return attachment