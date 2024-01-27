from fastapi import Depends, APIRouter, Path
from plm.schemas import PersonalNoteResponse, PersonalNoteCreate, PersonalNoteUpdate
from plm.models import PersonalNote
from plm.dependencies import get_db
from sqlmodel import Session, select
from plm.services.db import apply_patch
from plm.endpoints.helpers.personal_note_helpers import (
    get_personal_note_or_404,
    is_personal_note_name_unique,
    check_personal_note_types,
)
from plm.services.validation_exceptions import (
    raise_validation_exception,
)
from typing import List
from plm.enums import PersonalNoteTypes

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
    personal_note_entity.user_id = user_id

    if not is_personal_note_name_unique(db, personal_note_entity, user_id):
        raise_validation_exception(
            f"A personal note with this same name already exists."
        )

    check_personal_note_types(
        personal_note_entity,
        [
            PersonalNoteTypes.Description,
            PersonalNoteTypes.ProgressReport,
            PersonalNoteTypes.Observations,
        ],
    )

    db.add(personal_note_entity)
    db.commit()

    return personal_note_entity


@router.patch(
    path="/tasks/{userId}/{taskId}/personal-notes/{personalNoteId}",
    name="Update an existing note",
    response_model=PersonalNoteResponse,
    response_model_exclude_none=True,
)
def update_personal_note(
    payload: PersonalNoteUpdate,
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    personal_note_id: int = Path(alias="personalNoteId"),
    db: Session = Depends(get_db),
):
    personal_note_entity = get_personal_note_or_404(
        db, user_id, task_id, personal_note_id
    )

    if payload.name:
        personal_note_entity.name = payload.name
        if not is_personal_note_name_unique(db, personal_note_entity, user_id):
            raise_validation_exception(
                f"A personal note with this same name already exists."
            )

    apply_patch(personal_note_entity, payload)

    check_personal_note_types(
        personal_note_entity,
        [
            PersonalNoteTypes.Description,
            PersonalNoteTypes.ProgressReport,
            PersonalNoteTypes.Observations,
        ],
    )

    db.commit()

    return personal_note_entity


@router.delete(
    path="/tasks/{userId}/{taskId}/personal-notes/{personalNoteId}",
    name="Delete a personal note",
    status_code=204,
)
def delete_personal_note(
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    personal_note_id: int = Path(alias="personalNoteId"),
    db: Session = Depends(get_db),
) -> None:
    personal_note_entity = get_personal_note_or_404(
        db, user_id, task_id, personal_note_id
    )

    db.delete(personal_note_entity)
    db.commit()
