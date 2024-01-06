import logging

from sqlmodel import create_engine
from sqlalchemy import event
import sqlalchemy.sql.functions as funcs

# SQLModel uses the "future" engine (2.0).
from sqlalchemy.future import Engine

from plm.models import Entity
from plm.settings import PlmSettings
from plm.services.db.session_with_user import SessionWithUser


def get_engine(settings: PlmSettings) -> Engine:

    url = f"postgresql+psycopg2://{settings.db_username}@{settings.local_db_host}:{settings.local_db_port}/{settings.db_name}"
    logging.info(f"Using Postgres at {url}.")

    engine = create_engine(
        url=url,
        connect_args={"sslmode": "require" if not settings.db_password else "allow"},
    )

    @event.listens_for(engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams):
        password = settings.db_password
        cparams["password"] = password

    @event.listens_for(SessionWithUser, "before_flush")
    def before_flush(session: SessionWithUser, flush_context, instances):
        user = session.get_user()
        user_id = user.email

        if not user_id:
            user_id = user.id

        # Set created_by and created_on for new entities.
        for target in session.new:
            if isinstance(target, Entity):
                target.created_by = user_id
                target.created_on = funcs.now()

        # Set modified_by and modified_on for entities that have been updated.
        for target in session.dirty:
            if isinstance(target, Entity):
                target.modified_by = user_id
                target.modified_on = funcs.now()

    return engine
