from plm.models import CamelModel

from datetime import datetime

from typing import Optional


class PersonalNoteResponse(CamelModel):
    id: int
    name: str
    type: str
    note: str
    correspondence_email_address: str
    created_by: str
    created_on: datetime
    modified_by: Optional[str]
    modified_on: Optional[datetime]


class PersonalNoteCreate(CamelModel):
    name: str
    type: str
    note: str
    user_id: Optional[str]
    correspondence_email_address: str


class PersonalNoteUpdate(CamelModel):
    name: Optional[str]
    type: Optional[str]
    note: Optional[str]
