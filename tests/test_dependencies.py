from plm.dependencies import (
    initialize_dependencies,
    reset_dependencies,
    get_email_client,
    get_settings,
    get_auth0_user,
    get_calling_user,
    get_db,
    get_db_without_user,
    PermissionCheck,
)
from fastapi.exceptions import HTTPException
from plm.enums import Permission
from plm.security import User
from fastapi_auth0 import Auth0User
import pytest
from plm.settings import PlmSettings
from unittest.mock import MagicMock, AsyncMock, patch, ANY

# This is required because we have async tests.
@pytest.fixture
def anyio_backend():
    return "asyncio"


class MockSettings:
    def __init__(self, require_authentication, fake_user_is_admin):
        self.skip_authentication = not require_authentication
        self.skip_authentication_as_admin = fake_user_is_admin


def test_get_settings():
    reset_dependencies()

    try:
        settings = "settings"
        initialize_dependencies(settings, None)

        assert get_settings() == settings
    finally:
        reset_dependencies()


@pytest.mark.anyio
async def test_get_auth0_user():
    reset_dependencies()

    try:
        settings = MockSettings(True, True)
        fake_user = User("userid", "nobody@here.com", [Permission.Read])
        creds = "creds"
        mock_auth0 = MagicMock()
        mock_get_user = AsyncMock()
        mock_auth0.get_user = mock_get_user
        mock_get_user.return_value = fake_user
        initialize_dependencies(settings, None)

        user = await get_auth0_user(settings)

        mock_auth0.get_user.call_count == 1
    finally:
        reset_dependencies()


@pytest.mark.anyio
async def test_get_auth0_user_without_authentication():
    reset_dependencies()

    try:
        settings = MockSettings(False, False)
        creds = "creds"

        user = await get_auth0_user(settings)

        assert user.id == "dev"
        assert user.email == "dev@localhost"
        assert user.permissions == ["read:all", "admin:all"]
    finally:
        reset_dependencies()


@pytest.mark.anyio
async def test_get_auth0_user_without_authentication_as_admin():
    reset_dependencies()

    try:
        settings = MockSettings(False, True)
        creds = "creds"

        user = await get_auth0_user(settings)

        assert user.id == "dev"
        assert user.email == "dev@localhost"
        assert user.permissions == ["read:all", "admin:all"]
    finally:
        reset_dependencies()


@patch("plm.dependencies.EmailSenderClient")
def test_get_email_client(mock_email_client):
    reset_dependencies()

    try:
        mocked_client = MagicMock()
        mocked_client.starttls = MagicMock()
        settings = PlmSettings(
            db_username="user",
            db_name="name",
            local_db_host="host",
            local_db_port=513,
            db_password="password",
            smtp_server="server",
            smtp_port=123,
            plm_email_address="test@localhost.dev",
            plm_email_password="email-password",
        )
        initialize_dependencies(settings, None)
        mock_email_client.return_value.__enter__.return_value = mocked_client

        email_client = next(get_email_client(settings))

        assert email_client == mocked_client

    finally:
        reset_dependencies()


def test_get_calling_user():
    reset_dependencies()

    try:
        fake_user = Auth0User(sub="id", permissions=["perm"])
        fake_user.email = "email"

        user = get_calling_user(fake_user)

        assert user.id == "id"
        assert user.email == "email"
        assert user.permissions == ["perm"]
    finally:
        reset_dependencies()


@patch("plm.dependencies.SessionWithUser")
def test_get_db(mock_session):
    reset_dependencies()

    try:
        user = "user"
        session = MagicMock()
        engine = "engine"
        mock_session.return_value.__enter__.return_value = session
        initialize_dependencies(None, engine)

        db = next(get_db(user))

        mock_session.assert_called_once_with(engine)
        mock_session.return_value.__exit__.assert_called_once()
        assert db == session
        session.set_user.assert_called_once_with(user)
    finally:
        reset_dependencies()


@patch("plm.dependencies.Session")
def test_get_db_without_user(mock_session):
    reset_dependencies()

    try:
        session = "session"
        engine = "engine"
        mock_session.return_value.__enter__.return_value = session
        initialize_dependencies(None, engine)

        db = next(get_db_without_user())

        mock_session.assert_called_once_with(engine)
        mock_session.return_value.__exit__.assert_called_once()
        assert db == session
    finally:
        reset_dependencies()


def test_permission_check():
    checker = PermissionCheck(Permission.Admin)
    good_user = User(permissions=["other", str(Permission.Admin)])
    bad_user = User(permissions=["other"])

    checker.__call__(good_user)

    with pytest.raises(HTTPException) as excinfo:
        checker.__call__(bad_user)

    assert excinfo.value.status_code == 403
