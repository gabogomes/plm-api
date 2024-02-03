from fastapi import Depends, APIRouter, Path
from plm.models import PersonalNote
from plm.dependencies import get_db, get_email_client
from sqlmodel import Session, select
import smtplib
from plm.services.email_service import EmailSenderClient

router = APIRouter(prefix="/v1")


@router.post(
    path="/emails/{userId}/{taskId}",
    name="Send e-mail about a given task",
)
def send_email_notification(
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    db: Session = Depends(get_db),
    email_client: EmailSenderClient = Depends(get_email_client),
):

    subject = "Test Subject"

    body = "Test Body"

    email_client.sendmail(
        email_client.sender_email_address,
        "aulasconsultorias@gmail.com",
        f"Subject: {subject}\n\n{body}",
    )

    return True
