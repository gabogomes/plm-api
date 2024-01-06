from typing import List

from fastapi import Depends, APIRouter, Query
from sqlmodel import Session, select, text
import logging

from plm.dependencies import (
    get_db,
    PermissionCheck,
)
from plm.enums import Permission
from plm.models import SchemaVersion
from plm.schemas import SchemaVersionResponse

router = APIRouter(
    prefix="/v1/schema", dependencies=[Depends(PermissionCheck(Permission.Admin))]
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@router.get(
    "/versions",
    name="Get applied schema versions",
    response_model=List[SchemaVersionResponse],
)
def get_migration_versions(
    db: Session = Depends(get_db),
    max_count: int = Query(
        alias="maxCount", title="Max number of versions to return", ge=1, default=10
    ),
):
    found_table = db.exec(
        text(
            f"select exists(select 1 from information_schema.tables where table_name = '{SchemaVersion.__tablename__}')"
        )
    ).fetchall()[0][0]

    if not found_table:
        # If the table doesn't exist, we have run 0 migrations.
        return list()

    # We return them in descending order because the most recently applied migrations are
    # usually what a user is interested in.
    return db.exec(
        select(SchemaVersion)
        .distinct()
        .order_by(SchemaVersion.installed_rank.desc())
        .limit(max_count)
    ).fetchall()
