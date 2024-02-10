from unittest.mock import patch, MagicMock

import pytest

from plm.services.db.engine import get_engine
from plm.models import Entity
from plm.settings import PlmSettings
from plm.services.db.session_with_user import SessionWithUser


def get_url(host: str, port: int, db: str, user: str):
    return f"postgresql+psycopg2://{user}@{host}:{port}/{db}"


def get_settings(
    db_username=None,
    db_name=None,
    local_db_host=None,
    local_db_port=None,
    db_password=None,
    smtp_server=None,
    smtp_port=None,
    plm_email_address=None,
    plm_email_password=None,
):
    return PlmSettings(
        db_username=db_username,
        db_name=db_name,
        local_db_host=local_db_host,
        local_db_port=local_db_port,
        db_password=db_password,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        plm_email_address=plm_email_address,
        plm_email_password=plm_email_password,
    )


class MockUser:
    def __init__(self, id, email):
        self.id = id
        self.email = email


class MockSession:
    def __init__(self, user):
        self.user = user

    def get_user(self):
        return self.user


class MockEntity(Entity):
    pass


class MockNonEntity:
    pass


@patch("plm.services.db.engine.create_engine")
@patch("plm.services.db.engine.event")
@patch("sqlalchemy.sql.functions.now")
def test_set_created_and_modified_attributes_with_email(
    mock_now, mock_event, mock_create_engine
):
    engine = "engine"
    mock_create_engine.return_value = engine
    mock_now.return_value = "now"
    settings = get_settings(
        db_username="db_username",
        db_name="db_name",
        local_db_host="local_db_host",
        local_db_port=544,
        db_password="db_password",
        smtp_server="smtp_server",
        smtp_port=211,
        plm_email_address="plm_email_address",
        plm_email_password="plm_email_password",
    )

    created_engine = get_engine(settings)

    assert created_engine == engine

    assert mock_event.listens_for.call_count == 2
    assert mock_event.listens_for.call_args_list[0][0][0] == engine
    assert mock_event.listens_for.call_args_list[0][0][1] == "do_connect"
    assert mock_event.listens_for.call_args_list[1][0][0] == SessionWithUser
    assert mock_event.listens_for.call_args_list[1][0][1] == "before_flush"
    before_flush = mock_event.listens_for().mock_calls[1][1][0]

    new_entity = MockEntity()
    new_non_entity = MockNonEntity()
    dirty_entity = MockEntity()
    dirty_non_entity = MockNonEntity()
    user = MockUser("id", "email")
    session = MockSession(user)
    session.new = (
        new_entity,
        new_non_entity,
    )
    session.dirty = (
        dirty_entity,
        dirty_non_entity,
    )

    before_flush(session, "", [])

    assert new_entity.created_by == "email"
    assert new_entity.created_on == "now"

    with pytest.raises(AttributeError):
        assert new_non_entity.created_by == None

    with pytest.raises(AttributeError):
        assert new_non_entity.created_on == None

    assert dirty_entity.modified_by == "email"
    assert dirty_entity.modified_on == "now"

    with pytest.raises(AttributeError):
        assert dirty_non_entity.modified_by == None

    with pytest.raises(AttributeError):
        assert dirty_non_entity.modified_on == None


@patch("plm.services.db.engine.create_engine")
@patch("plm.services.db.engine.event")
@patch("sqlalchemy.sql.functions.now")
def test_set_created_and_modified_attributes_without_email(
    mock_now, mock_event, mock_create_engine
):
    engine = "engine"
    mock_create_engine.return_value = engine
    mock_now.return_value = "now"
    settings = get_settings(
        db_username="db_username",
        db_name="db_name",
        local_db_host="local_db_host",
        local_db_port=544,
        db_password="db_password",
        smtp_server="smtp_server",
        smtp_port=211,
        plm_email_address="plm_email_address",
        plm_email_password="plm_email_password",
    )

    created_engine = get_engine(settings)

    assert created_engine == engine

    assert mock_event.listens_for.call_count == 2
    assert mock_event.listens_for.call_args_list[0][0][0] == engine
    assert mock_event.listens_for.call_args_list[0][0][1] == "do_connect"
    assert mock_event.listens_for.call_args_list[1][0][0] == SessionWithUser
    assert mock_event.listens_for.call_args_list[1][0][1] == "before_flush"
    before_flush = mock_event.listens_for().mock_calls[1][1][0]

    new_entity = MockEntity()
    new_non_entity = MockNonEntity()
    dirty_entity = MockEntity()
    dirty_non_entity = MockNonEntity()
    user = MockUser("id", None)
    session = MockSession(user)
    session.new = (
        new_entity,
        new_non_entity,
    )
    session.dirty = (
        dirty_entity,
        dirty_non_entity,
    )

    before_flush(session, "", [])

    assert new_entity.created_by == "id"
    assert new_entity.created_on == "now"

    with pytest.raises(AttributeError):
        assert new_non_entity.created_by == None

    with pytest.raises(AttributeError):
        assert new_non_entity.created_on == None

    assert dirty_entity.modified_by == "id"
    assert dirty_entity.modified_on == "now"

    with pytest.raises(AttributeError):
        assert dirty_non_entity.modified_by == None

    with pytest.raises(AttributeError):
        assert dirty_non_entity.modified_on == None


@patch("plm.services.db.engine.create_engine")
@patch("plm.services.db.engine.event")
def test_get_engine_with_password(mock_event, mock_create_engine):
    mock_rds_client = MagicMock()
    mock_generate_token = MagicMock()
    mock_rds_client.generate_db_auth_token = mock_generate_token
    engine = "engine"
    mock_create_engine.return_value = engine
    settings = get_settings(
        db_username="db_username",
        db_name="db_name",
        local_db_host="local_db_host",
        local_db_port=544,
        db_password="db_password",
        smtp_server="smtp_server",
        smtp_port=211,
        plm_email_address="plm_email_address",
        plm_email_password="plm_email_password",
    )

    created_engine = get_engine(settings)

    assert created_engine == engine
    url = get_url("local_db_host", 544, "db_name", "db_username")
    mock_create_engine.assert_called_once_with(
        url=url, connect_args={"sslmode": "allow"}
    )

    assert mock_event.listens_for.call_count == 2
    assert mock_event.listens_for.call_args_list[0][0][0] == engine
    assert mock_event.listens_for.call_args_list[0][0][1] == "do_connect"
    assert mock_event.listens_for.call_args_list[1][0][0] == SessionWithUser
    assert mock_event.listens_for.call_args_list[1][0][1] == "before_flush"
    provide_token = mock_event.listens_for().mock_calls[0][1][0]

    mock_generate_token.assert_not_called()

    # Test to make sure we use the configured password.
    cparams = {}
    provide_token("", "", "", cparams)
    assert cparams["password"] == "db_password"
    mock_generate_token.assert_not_called()
