from sqlmodel import Session, and_
from plm.models import Task
from fastapi import HTTPException
from plm.enums import TaskStatus, TaskTypes
from typing import List
from plm.services.validation_exceptions import (
    raise_validation_exception,
)


def get_task_or_404(db: Session, user_id: str, task_id: int) -> Task:
    task_entity = (
        db.query(Task)
        .where(and_(Task.user_id == user_id, Task.id == task_id))
        .one_or_none()
    )

    if not task_entity:
        raise HTTPException(404)

    return task_entity


def is_task_name_unique(db: Session, task_entity: Task, user_id: str) -> bool:
    task_name = task_entity.name

    existing_task = (
        db.query(Task).filter(Task.name == task_name, Task.user_id == user_id).first()
    )

    return True if existing_task is None else False


def check_task_status(task_entity: Task, allowed_statuses: List[TaskStatus]) -> None:
    if task_entity.status not in allowed_statuses:
        raise_validation_exception(
            f"The task has a status of {task_entity.status}, which is not allowed."
        )


def check_task_types(task_entity: Task, allowed_types: List[TaskTypes]) -> None:
    if task_entity.type not in allowed_types:
        raise_validation_exception(
            f"The task has a type of {task_entity.type}, which is not allowed."
        )
