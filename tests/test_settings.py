import os
from unittest.mock import patch

import pytest

from plm.settings import PlmSettings

env_vars = {
    "DB_USERNAME": "test_username",
    "DB_NAME": "test_db_name",
    "LOCAL_DB_HOST": "test_db_host",
    "LOCAL_DB_PORT": "5000",
    "DB_PASSWORD": "test_db_password",
    "SMTP_SERVER": "test_smtp_server",
    "SMTP_PORT": "111",
    "PLM_EMAIL_ADDRESS": "test_email_address",
    "PLM_EMAIL_PASSWORD": "test_email_password",
}


def test_raises_if_missing_environment_variable():
    with pytest.raises(Exception):
        with patch.dict(os.environ, env_vars):
            del os.environ["DB_USERNAME"]
            PlmSettings()


def test_all_values():
    with patch.dict(os.environ, env_vars):
        sut = PlmSettings()

    assert sut.db_username == "test_username"
    assert sut.db_name == "test_db_name"
    assert sut.local_db_host == "test_db_host"
    assert sut.local_db_port == 5000
    assert sut.db_password == "test_db_password"
    assert sut.smtp_server == "test_smtp_server"
    assert sut.smtp_port == 111
    assert sut.plm_email_address == "test_email_address"
    assert sut.plm_email_password == "test_email_password"
