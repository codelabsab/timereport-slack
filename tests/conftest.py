import os
from unittest import mock

import pytest
from chalice.config import Config
from chalice.local import LocalGateway

signing_secret = "fake_secret"


@pytest.fixture
@mock.patch.dict(
    os.environ,
    {"signing_secret": "fake_secret", "backend_url": "http://localhost:8010/v1"},
)
def chalice_app():
    from app import app

    return LocalGateway(app, Config())
