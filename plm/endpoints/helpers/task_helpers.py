from sqlmodel import Session, and_
from plm.models import Task
from fastapi import HTTPException


def get_task_or_404(db: Session, user_id: str, task_id: int) -> Task:
    task_entity = (
        db.query(Task)
        .where(and_(Task.user_id == user_id, Task.id == task_id))
        .one_or_none()
    )

    if not task_entity:
        raise HTTPException(404)

    return task_entity
