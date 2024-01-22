from fastapi import Depends, APIRouter, Path
from plm.schemas import PersonalNoteResponse, PersonalNoteCreate, PersonalNoteUpdate
from plm.models import PersonalNote
from plm.dependencies import get_db
from sqlmodel import Session, select
from plm.services.db import apply_patch
from plm.endpoints.helpers.personal_note_helpers import (
    get_personal_note_or_404,
    is_personal_note_name_unique,
)
from plm.services.validation_exceptions import (
    raise_validation_exception,
)
from typing import List

router = APIRouter(prefix="/v1")


@router.get(
    path="/tasks/{userId}/{taskId}/personal-notes",
    name="Get all personal notes for a given user and task",
    response_model=List[PersonalNoteResponse],
    response_model_exclude_none=True,
)
def get_personal_notes(
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    db: Session = Depends(get_db),
):

    query = db.exec(
        select(PersonalNote).filter(
            PersonalNote.user_id == user_id, PersonalNote.task_id == task_id
        )
    ).all()

    return query


@router.get(
    path="/tasks/{userId}/{taskId}/personal-notes/{personalNoteId}",
    name="Get a given personal note by personal note id",
    response_model=PersonalNoteResponse,
    response_model_exclude_none=True,
)
def get_personal_note(
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    personal_note_id: int = Path(alias="personalNoteId"),
    db: Session = Depends(get_db),
):

    query = get_personal_note_or_404(db, user_id, task_id, personal_note_id)

    return query


@router.post(
    path="/tasks/{userId}/{taskId}/personal-notes/",
    name="Create new personal note for a given task",
    response_model=PersonalNoteResponse,
    response_model_exclude_none=True,
)
def create_personal_note(
    payload: PersonalNoteCreate,
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    db: Session = Depends(get_db),
):
    personal_note_entity = PersonalNote.parse_obj(payload)
    personal_note_entity.task_id = task_id

    if not is_personal_note_name_unique(db, personal_note_entity, user_id):
        raise_validation_exception(
            f"A personal note with this same name already exists."
        )

    db.add(personal_note_entity)
    db.commit()

    return personal_note_entity


"""
@router.patch(
    path="/tasks/{userId}/{taskId}",
    name="Update an existing task",
    response_model=TaskResponse,
    response_model_exclude_none=True,
)
def update_task(
    payload: TaskUpdate,
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    db: Session = Depends(get_db),
):
    task_entity = get_task_or_404(db, user_id, task_id)

    if payload.name:
        task_entity.name = payload.name
        if not is_task_name_unique(db, task_entity):
            raise_validation_exception(f"A task with this same name already exists.")

    apply_patch(task_entity, payload)

    db.commit()

    return task_entity


@router.delete(path="/tasks/{userId}/{taskId}", name="Delete a task", status_code=204)
def delete_task(
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    db: Session = Depends(get_db),
) -> None:
    task_entity = get_task_or_404(db, user_id, task_id)

    db.delete(task_entity)
    db.commit()
"""
