import sys
import logging

from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

load_dotenv()

from fastapi import FastAPI, Depends, Request, status
from fastapi_pagination import add_pagination

from plm.settings import PlmSettings
from plm.services.db import get_engine
from plm.dependencies import initialize_dependencies
from plm.endpoints.v1.health import router as health_router
from plm.endpoints.v1.migration import router as migration_router
from plm.endpoints.v1.task import router as task_router
from plm.endpoints.v1.personal_note import router as personal_note_router

try:
    settings = PlmSettings()
except Exception as e:
    logging.exception("Unable to load settings, check the environment.")
    sys.exit(1)

engine = get_engine(settings)

initialize_dependencies(settings, engine)

app = FastAPI(
    title="Personal Life Manager API",
    docs_url="/docs",
    root_path="/",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    errors = [
        {"loc": err["loc"], "message": err["msg"], "type": err["type"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": errors}),
    )


add_pagination(app)

app.include_router(health_router, tags=["Health"])
app.include_router(migration_router, tags=["Schema Migration"])
app.include_router(task_router, tags=["Tasks"])
app.include_router(personal_note_router, tags=["Personal Notes"])

logging.getLogger().setLevel(logging.INFO)
