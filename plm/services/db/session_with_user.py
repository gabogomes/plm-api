from sqlmodel import Session

from plm.security import User


class SessionWithUser(Session):
    def __init__(self, started_engine):
        super().__init__(started_engine, autoflush=False)
        self.user = None

    def set_user(self, user: User):
        self.user = user

    def get_user(self) -> User:
        return self.user
