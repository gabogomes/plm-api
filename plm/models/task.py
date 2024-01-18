from plm.models import Entity


class Task(Entity, table=True):
    __tablename__ = "task"

    name: str
    status: str
    type: str
    user_id: str
    correspondence_email_address: str
