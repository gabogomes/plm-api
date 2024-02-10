from plm.models import PersonalNote
from unittest.mock import patch, MagicMock
from plm.enums import PersonalNoteTypes
import pytest
from plm.endpoints.v1.personal_note import router
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime
from plm.dependencies import get_db
from tests.dependency_mocker import DependencyMocker
from tests.db_helpers import assert_wheres_are_equal
from sqlmodel import and_
import copy

app = FastAPI()
app.include_router(router)
client = TestClient(app)

now = datetime.now()

fake_personal_note = PersonalNote(
    id=1,
    created_by="test@localdev.com",
    created_on=now,
    task_id=1,
    name="Personal Note 1",
    type=PersonalNoteTypes.ProgressReport,
    note="This is a sample note",
    user_id="user-1",
    correspondence_email_address="address@email.com",
)


fake_payload = {
    "name": "Personal Note 1",
    "type": "Observations",
    "note": "This is a sample note",
    "user_id": "user-1",
    "correspondence_email_address": "address@email.com",
}


@pytest.fixture()
def mock_select():
    with patch("plm.endpoints.v1.personal_note.select") as m:
        yield m


def test_get_all_personal_notes():
    mock_db = MagicMock()
    mock_db.exec.return_value.all.return_value = [fake_personal_note]

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.get("/v1/tasks/user-1/1/personal-notes")

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 1
    assert json_response[0]["createdBy"] == fake_personal_note.created_by


def test_get_one_personal_note():
    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = (
        fake_personal_note
    )

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.get("/v1/tasks/user-1/1/personal-notes/1")

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["correspondenceEmailAddress"] == "address@email.com"
    assert_wheres_are_equal(
        mock_db.query.return_value.where,
        0,
        and_(
            PersonalNote.user_id == "user-1",
            PersonalNote.task_id == 1,
            PersonalNote.id == 1,
        ),
    )


def test_get_one_personal_note_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.get("/v1/tasks/user-1/1/personal-notes/1")

    assert response.status_code == 404


@patch("plm.models.personal_note.PersonalNote.parse_obj")
def test_create_personal_note_successful(mock_parse_obj):
    fake_personal_note_to_create = copy.copy(fake_personal_note)
    mock_parse_obj.return_value = fake_personal_note
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.post("/v1/tasks/user-1/1/personal-notes", json=fake_payload)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["note"] == "This is a sample note"
    mock_db.add.assert_called_once_with(fake_personal_note_to_create)
    mock_db.commit.assert_called_once_with()


@patch("plm.models.personal_note.PersonalNote.parse_obj")
def test_create_personal_note_error_due_to_existing_name(mock_parse_obj):
    fake_personal_note_to_create = copy.copy(fake_personal_note)
    mock_parse_obj.return_value = fake_personal_note
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = (
        fake_personal_note
    )

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.post("/v1/tasks/user-1/1/personal-notes", json=fake_payload)

    assert response.status_code == 400
    json_response = response.json()
    assert (
        json_response["detail"][0]["message"]
        == f"A personal note with this same name already exists."
    )
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


@patch("plm.models.personal_note.PersonalNote.parse_obj")
def test_create_personal_note_error_due_to_unknown_type(mock_parse_obj):
    fake_personal_note_to_create = copy.copy(fake_personal_note)
    fake_personal_note_to_create.type = "Unknown Type"
    mock_parse_obj.return_value = fake_personal_note_to_create
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.post("/v1/tasks/user-1/1/personal-notes", json=fake_payload)

    assert response.status_code == 400
    json_response = response.json()
    assert (
        json_response["detail"][0]["message"]
        == f"The note has a type of Unknown Type, which is not allowed."
    )
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


def test_update_personal_note_successful():
    fake_personal_note_to_update = copy.copy(fake_personal_note)
    fake_personal_note_to_update.type = "Description"
    this_fake_payload = {}
    this_fake_payload["name"] = "Personal Note 2"

    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = (
        fake_personal_note_to_update
    )
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.patch(
            "/v1/tasks/user-1/1/personal-notes/1", json=this_fake_payload
        )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["name"] == "Personal Note 2"
    mock_db.commit.assert_called_once_with()
    assert_wheres_are_equal(
        mock_db.query.return_value.where,
        0,
        and_(
            PersonalNote.user_id == "user-1",
            PersonalNote.task_id == 1,
            PersonalNote.id == 1,
        ),
    )


def test_update_personal_note_error_due_to_existing_name():
    fake_personal_note_to_update = copy.copy(fake_personal_note)
    fake_personal_note_to_update.type = "Description"
    this_fake_payload = {}
    this_fake_payload["name"] = "Personal Note 2"

    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = (
        fake_personal_note_to_update
    )
    mock_db.query.return_value.filter.return_value.first.return_value = (
        fake_personal_note_to_update
    )

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.patch(
            "/v1/tasks/user-1/1/personal-notes/1", json=this_fake_payload
        )

    assert response.status_code == 400
    json_response = response.json()
    assert (
        json_response["detail"][0]["message"]
        == "A personal note with this same name already exists."
    )
    mock_db.commit.assert_not_called()
    assert_wheres_are_equal(
        mock_db.query.return_value.where,
        0,
        and_(
            PersonalNote.user_id == "user-1",
            PersonalNote.task_id == 1,
            PersonalNote.id == 1,
        ),
    )


def test_update_personal_note_error_due_to_unknown_type_in_payload():
    fake_personal_note_to_update = copy.copy(fake_personal_note)
    fake_personal_note_to_update.type = "Description"
    this_fake_payload = {}
    this_fake_payload["type"] = "Unknown Type"

    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = (
        fake_personal_note_to_update
    )
    mock_db.query.return_value.filter.return_value.first.return_value = (
        fake_personal_note_to_update
    )

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.patch(
            "/v1/tasks/user-1/1/personal-notes/1", json=this_fake_payload
        )

    assert response.status_code == 400
    json_response = response.json()
    assert (
        json_response["detail"][0]["message"]
        == "The note has a type of Unknown Type, which is not allowed."
    )
    mock_db.commit.assert_not_called()
    assert_wheres_are_equal(
        mock_db.query.return_value.where,
        0,
        and_(
            PersonalNote.user_id == "user-1",
            PersonalNote.task_id == 1,
            PersonalNote.id == 1,
        ),
    )


def test_delete_personal_note_successful():
    existing_personal_note = copy.copy(fake_personal_note)
    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = (
        existing_personal_note
    )

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.delete("/v1/tasks/user-1/1/personal-notes/1")

    assert response.status_code == 204
    mock_db.delete.assert_called_once_with(existing_personal_note)
    mock_db.commit.assert_called_once_with()


def test_delete_personal_note_error_due_to_personal_note_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.delete("/v1/tasks/user-1/1/personal-notes/1")

    assert response.status_code == 404
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()
