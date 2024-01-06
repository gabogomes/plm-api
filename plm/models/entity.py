from datetime import datetime
from typing import Optional
from sqlmodel import Field

from plm.models import CamelModel


class Entity(CamelModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: Optional[str]
    created_on: Optional[datetime]
    modified_by: Optional[str]
    modified_on: Optional[datetime]
