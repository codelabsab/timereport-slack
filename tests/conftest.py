from unittest import mock

import pytest
from chalice.config import Config
import os
from chalice.local import LocalGateway

signing_secret = "fake_secret"


@pytest.fixture
@mock.patch.dict(os.environ, {"signing_secret": "fake_secret"})
def chalice_app():
    from app import app

    return LocalGateway(app, Config())
