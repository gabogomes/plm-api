from typing import List
from plm.models import Entity
from sqlmodel import Relationship


class Task(Entity, table=True):
    __tablename__ = "task"

    name: str
    status: str
    type: str
    user_id: str
    correspondence_email_address: str
    personal_notes: List["PersonalNote"] = Relationship(back_populates="task")
