import logging
import smtplib

from fastapi import Depends, HTTPException
from fastapi_auth0 import Auth0User
from sqlmodel import Session
from sqlalchemy.future import Engine

from plm.security import User
from plm.enums import Permission
from plm.services.db import SessionWithUser
from plm.services.email_service import EmailSenderClient
from plm.settings import PlmSettings

_dependencies = {}


def initialize_dependencies(
    settings: PlmSettings,
    engine: Engine,
):
    _dependencies["settings"] = settings
    _dependencies["engine"] = engine


def reset_dependencies():
    # This should only be called from unit tests.
    _dependencies = {}


def get_settings():
    return _dependencies["settings"]


def get_email_client(
    settings: PlmSettings = Depends(get_settings),
) -> EmailSenderClient:
    smtp_server = settings.smtp_server
    smtp_port = settings.smtp_port
    smtp_username = settings.plm_email_address
    smtp_password = settings.plm_email_password

    with EmailSenderClient(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.set_sender_email_address(smtp_username)
        yield smtp


async def get_auth0_user(settings: PlmSettings = Depends(get_settings)) -> Auth0User:
    permissions = [str(Permission.Read), str(Permission.Admin)]
    local_admin = Auth0User(sub="dev", permissions=permissions)
    local_admin.email = "dev@localhost"
    return local_admin


def get_calling_user(auth0_user: Auth0User = Depends(get_auth0_user)) -> User:
    return User(
        id=auth0_user.id,
        email=auth0_user.email,
        permissions=auth0_user.permissions,
    )


def get_db(user: User = Depends(get_calling_user)) -> SessionWithUser:
    with SessionWithUser(_dependencies["engine"]) as session:
        logging.debug("Created a new DB session.")
        session.set_user(user)
        yield session


def get_db_without_user() -> Session:
    with Session(_dependencies["engine"]) as session:
        yield session


class PermissionCheck:
    def __init__(self, required_permission: Permission):
        self.required_permission = required_permission

    def __call__(self, user: User = Depends(get_calling_user)):
        # Use str() so we can compare the enum value to the string in the JWT.
        if str(self.required_permission) not in user.permissions:
            raise HTTPException(
                403, f"User does not have permission {self.required_permission}."
            )
