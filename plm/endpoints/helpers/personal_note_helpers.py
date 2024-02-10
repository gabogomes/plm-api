from sqlmodel import Session, and_
from plm.models import PersonalNote
from fastapi import HTTPException
from plm.enums import PersonalNoteTypes
from typing import List
from plm.services.validation_exceptions import (
    raise_validation_exception,
)


def get_personal_note_or_404(
    db: Session, user_id: str, task_id: int, personal_note_id: int
) -> PersonalNote:
    personal_note_entity = (
        db.query(PersonalNote)
        .where(
            and_(
                PersonalNote.user_id == user_id,
                PersonalNote.task_id == task_id,
                PersonalNote.id == personal_note_id,
            )
        )
        .one_or_none()
    )

    if not personal_note_entity:
        raise HTTPException(404)

    return personal_note_entity


def is_personal_note_name_unique(
    db: Session, personal_note_entity: PersonalNote, user_id: str
) -> bool:
    personal_note_name = personal_note_entity.name

    existing_personal_note = (
        db.query(PersonalNote)
        .filter(
            and_(
                PersonalNote.name == personal_note_name, PersonalNote.user_id == user_id
            )
        )
        .first()
    )

    return True if existing_personal_note is None else False


def check_personal_note_types(
    personal_note_entity: PersonalNote, allowed_types: List[PersonalNoteTypes]
) -> None:
    if personal_note_entity.type not in allowed_types:
        raise_validation_exception(
            f"The note has a type of {personal_note_entity.type}, which is not allowed."
        )
