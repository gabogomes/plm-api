from fastapi import Depends, APIRouter, Path
from plm.models import PersonalNote
from plm.dependencies import get_db, get_email_client
from sqlmodel import Session, select
from plm.services.email_service import EmailSenderClient
from plm.endpoints.helpers.task_helpers import get_task_or_404

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

    task = get_task_or_404(db, user_id, task_id)

    personal_notes = db.exec(
        select(PersonalNote).where(PersonalNote.task_id == task_id)
    ).all()

    subject = f"PLM Reminder: {task.name}"

    body = "Personal Notes:\n"
    for note in personal_notes:
        body += f"\nPersonal Note Name: {note.name}\n"
        body += f"Personal Note Type: {note.type}\n"
        body += f"Personal Note Description: {note.note}\n"

    message_body = f"Subject: {subject}\n\n{body}"

    email_client.sendmail(
        from_addr=email_client.sender_email_address,
        to_addrs=task.correspondence_email_address,
        msg=message_body,
    )

    return {"message": f"Email sent successfully for Task named {task.name}"}
