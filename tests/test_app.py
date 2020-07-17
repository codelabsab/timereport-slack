import random

import pytest
from tests.utils import call_from_slack, get_raw_block_text, respond_interactively


def test_help_command(chalice_app):
    r = call_from_slack(
        chalice_app=chalice_app,
        full_command="help",
        user_id=f"{random.randint(0, 10000)}",
        user_name="mattias",
    )

    assert r["response"]["statusCode"] == 200
    assert "Supported actions are:" in r["slack_message"][1]["json"]["text"]


@pytest.mark.integration
def test_empty_list(chalice_app):
    r = call_from_slack(
        chalice_app=chalice_app,
        full_command="list today",
        user_id=f"{random.randint(0, 10000)}",
        user_name="mattias",
    )

    assert r["response"]["statusCode"] == 200
    assert "nothing to list" in r["slack_message"][1]["json"]["text"]


@pytest.mark.integration
def test_add_command_accepted(chalice_app):
    user_id = f"{random.randint(0, 10000)}"
    r = call_from_slack(
        chalice_app=chalice_app,
        full_command="add vab today 8",
        user_id=user_id,
        user_name="mattias",
    )

    assert r["response"]["statusCode"] == 200
    assert r["slack_message"][1]["json"]["text"] == "From timereport"
    attachments = r["slack_message"][1]["json"]["attachments"]
    assert attachments is not None
    attachment = attachments[0]
    assert attachment["actions"]
    assert "Submit" in attachment["title"]

    ri = respond_interactively(
        chalice_app=chalice_app,
        attachments=attachments,
        user_id=user_id,
        user_name="mattias",
    )
    assert ri["response"]["statusCode"] == 200
    assert ri["slack_message"][1]["json"]["text"] == "Added successfully"

    rl = call_from_slack(
        chalice_app=chalice_app,
        full_command="list today",
        user_id=user_id,
        user_name="mattias",
    )
    assert rl["response"]["statusCode"] == 200
    assert "nothing to list" not in rl["slack_message"][1]["json"]["text"]
    assert "Reason: *vab*" in get_raw_block_text(slack_message=rl["slack_message"])

    # Delete report
    r = call_from_slack(
        chalice_app=chalice_app,
        full_command="delete today",
        user_id=user_id,
        user_name="mattias",
    )

    assert r["response"]["statusCode"] == 200
    assert r["slack_message"][1]["json"]["text"] == "From timereport"

    attachments = r["slack_message"][1]["json"]["attachments"]
    assert attachments is not None
    attachment = attachments[0]
    assert attachment["actions"]
    assert "Delete" in attachment["title"]

    ri = respond_interactively(
        chalice_app=chalice_app,
        attachments=attachments,
        user_id=user_id,
        user_name="mattias",
    )
    assert ri["response"]["statusCode"] == 200
    assert "OK, hang on" in ri["slack_message"][1]["json"]["text"]


@pytest.mark.integration
def test_add_command_rejected(chalice_app):
    user_id = f"{random.randint(0, 10000)}"
    r = call_from_slack(
        chalice_app=chalice_app,
        full_command="add vab today 8",
        user_id=user_id,
        user_name="mattias",
    )

    assert r["response"]["statusCode"] == 200
    assert r["slack_message"][1]["json"]["text"] == "From timereport"
    attachments = r["slack_message"][1]["json"]["attachments"]
    assert attachments is not None
    attachment = attachments[0]
    assert attachment["actions"]
    assert "Submit" in attachment["title"]

    ri = respond_interactively(
        chalice_app=chalice_app,
        attachments=attachments,
        user_id=user_id,
        user_name="mattias",
        action="submit_no",
    )
    assert ri["response"]["statusCode"] == 200
    assert "canceled" in ri["slack_message"][1]["json"]["text"]


@pytest.mark.integration
def test_lock_month_and_list(chalice_app):
    user_id = f"{random.randint(0, 10000)}"
    r = call_from_slack(
        chalice_app=chalice_app,
        full_command="lock 2020-07",
        user_id=user_id,
        user_name="mattias",
    )
    assert r["response"]["statusCode"] == 200
    assert "Lock successful" in r["slack_message"][1]["json"]["text"]

    r = call_from_slack(
        chalice_app=chalice_app,
        full_command="lock list 2020",
        user_id=user_id,
        user_name="mattias",
    )
    assert r["response"]["statusCode"] == 200

    raw_block_text = get_raw_block_text(slack_message=r["slack_message"])
    assert "Locks found for months in" in raw_block_text
    assert "2020-07" in raw_block_text
