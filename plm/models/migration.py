from datetime import datetime

from sqlmodel import Field

from plm.models import CamelModel


class SchemaVersion(CamelModel, table=True):
    __tablename__ = "flyway_schema_history"

    installed_rank: int = Field(primary_key=True)
    version: str
    description: str
    type: str
    script: str
    checksum: int
    installed_by: str
    installed_on: datetime
