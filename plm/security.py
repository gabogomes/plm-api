from typing import List


class User:
    id: str
    email: str
    permissions: List[str]

    def __init__(
        self,
        id: str = None,
        email: str = None,
        permissions: List[str] = None,
    ):
        self.id = id
        self.email = email
        self.permissions = permissions
