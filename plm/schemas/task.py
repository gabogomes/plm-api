from plm.models import CamelModel

from datetime import datetime

from typing import Optional


class TaskResponse(CamelModel):
    id: int
    name: str
    status: str
    type: str
    correspondence_email_address: str
    created_by: str
    created_on: datetime
    modified_by: Optional[str]
    modified_on: Optional[datetime]


class TaskCreate(CamelModel):
    name: str
    status: str
    type: str
    user_id: str
    correspondence_email_address: str


class TaskUpdate(CamelModel):
    name: Optional[str]
    status: Optional[str]
    type: Optional[str]
