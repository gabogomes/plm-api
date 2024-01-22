from plm.models import Entity, Task
from sqlmodel import Relationship, Field


class PersonalNote(Entity, table=True):
    __tablename__ = "personal_note"

    task_id: int = Field(default=None, foreign_key="task.id")
    name: str
    type: str
    note: str
    user_id: str
    correspondence_email_address: str
    task: Task = Relationship(back_populates="personal_notes")
