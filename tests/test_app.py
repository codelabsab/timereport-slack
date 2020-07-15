from tests.utils import call_from_slack


def test_help_command(chalice_app):
    r = call_from_slack(chalice_app, ["help"], "1234", "mattias")

    assert r["response"]["statusCode"] == 200
    assert "Supported actions are:" in r["slack_message"]
