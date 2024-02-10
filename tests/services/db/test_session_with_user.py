from unittest.mock import patch

from plm.services.db.session_with_user import SessionWithUser


@patch("plm.services.db.session_with_user.Session.__init__")
def test_session_with_user(mock_init):
    engine = "engine"
    user = "user"

    session = SessionWithUser(engine)
    session.set_user(user)
    returned_user = session.get_user()

    mock_init.assert_called_once_with(engine, autoflush=False)
    assert returned_user == user
