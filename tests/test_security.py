from plm.security import User
from plm.enums import Permission


def test_user():
    user = User(id="id", email="email", permissions=["a", "b"])
    assert user.id == "id"
    assert user.email == "email"
    assert user.permissions == ["a", "b"]


def test_permission_compare():
    user = User(id="id", email="email", permissions=["read:all"])
    assert Permission.Read in user.permissions
    assert Permission.Admin not in user.permissions
    assert str(Permission.Read) == "read:all"
    assert str(Permission.Admin) == "admin:all"
