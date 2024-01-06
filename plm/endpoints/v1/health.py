import logging

from fastapi import Response, Depends, APIRouter
from sqlmodel import Session

from plm.dependencies import get_db_without_user

router = APIRouter(prefix="/v1")


@router.get(
    "/healthcheck",
    name="Healthcheck",
    description="Returns 200 on success, 500 if something is wrong",
)
def healthcheck(response: Response, db: Session = Depends(get_db_without_user)):
    """
    Returns the health of the API.
    """
    all_ok = True
    result = {"postgres": "OK"}

    try:
        db.execute("select 1").fetchall()
    except Exception as e:
        all_ok = False
        result["postgres"] = "FAIL"
        result["postgres_error"] = str(e)
        logging.exception("Unable to connect to Postgres")

    response.status_code = 200 if all_ok else 500
    return result
