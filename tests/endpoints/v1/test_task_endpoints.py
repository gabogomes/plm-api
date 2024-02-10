from plm.models import Task
from unittest.mock import patch, MagicMock
from plm.enums import TaskStatus, TaskTypes
import pytest
from plm.endpoints.v1.task import router
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

fake_task = Task(
    id=1,
    created_by="test@localdev.com",
    created_on=now,
    name="Task 1",
    status=TaskStatus.ToDo,
    type=TaskTypes.Work,
    user_id="user-1",
    correspondence_email_address="user@email.com",
)


fake_payload = {
    "name": "Task 1",
    "status": "To Do",
    "type": "Work",
    "user_id": "user-1",
    "correspondence_email_address": "user@email.com",
}


@pytest.fixture()
def mock_paginate():
    with patch("plm.endpoints.v1.task.paginate") as mock_paginate:
        mock_paginate.return_value = {
            "items": [fake_task],
            "total": 1,
            "limit": 1,
            "offset": 1,
        }
        yield mock_paginate


@pytest.fixture()
def mock_select():
    with patch("plm.endpoints.v1.task.select") as m:
        yield m


def test_get_all_tasks(mock_paginate, mock_select):
    mock_db = MagicMock()

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.get("/v1/tasks/user-1")

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response["items"]) == 1
    assert json_response["items"][0]["createdBy"] == fake_task.created_by
    mock_select.assert_called_once_with(Task)
    mock_select.return_value.filter.return_value.order_by.assert_called_once_with(
        Task.id
    )
    mock_paginate.assert_called_once_with(
        mock_db, mock_select.return_value.filter.return_value.order_by.return_value
    )


def test_get_one_task_found():
    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = fake_task

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.get("/v1/tasks/user-1/1")

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["name"] == fake_task.name
    mock_db.query.assert_called_once_with(Task)
    assert_wheres_are_equal(
        mock_db.query.return_value.where,
        0,
        and_(Task.user_id == "user-1", Task.id == 1),
    )


def test_get_one_task_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.where.return_value.one_or_none.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.get("/v1/tasks/user-1/1")

    assert response.status_code == 404


@patch("plm.models.task.Task.parse_obj")
def test_create_task_successful(mock_parse_obj):
    fake_task_to_create = copy.copy(fake_task)
    mock_parse_obj.return_value = fake_task_to_create
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.post("/v1/tasks/user-1", json=fake_payload)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["id"] == 1
    assert json_response["name"] == fake_task.name
    assert json_response["status"] == "To Do"
    mock_db.add.assert_called_once_with(fake_task_to_create)
    mock_db.commit.assert_called_once_with()


@patch("plm.models.task.Task.parse_obj")
def test_create_task_error_due_to_non_unique_name(mock_parse_obj):
    fake_task_to_create = copy.copy(fake_task)
    mock_parse_obj.return_value = fake_task_to_create
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = fake_task

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.post("/v1/tasks/user-1", json=fake_payload)

    assert response.status_code == 400
    json_response = response.json()
    assert (
        json_response["detail"][0]["message"]
        == f"A task with this same name already exists."
    )
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


@patch("plm.models.task.Task.parse_obj")
def test_create_task_error_due_to_unknown_status(mock_parse_obj):
    fake_task_to_create = copy.copy(fake_task)
    fake_task_to_create.status = "Unknown Status"
    mock_parse_obj.return_value = fake_task_to_create
    fake_payload["status"] = "Unknown Status"
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.post("/v1/tasks/user-1", json=fake_payload)

    assert response.status_code == 400
    json_response = response.json()
    assert (
        json_response["detail"][0]["message"]
        == f"The task has a status of Unknown Status, which is not allowed."
    )
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


@patch("plm.models.task.Task.parse_obj")
def test_create_task_error_due_to_unknown_type(mock_parse_obj):
    fake_task_to_create = copy.copy(fake_task)
    fake_task_to_create.status = "To Do"
    fake_task_to_create.type = "Unknown Type"
    mock_parse_obj.return_value = fake_task_to_create
    fake_payload["status"] = "To Do"
    fake_payload["type"] = "Unknown Type"
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with DependencyMocker(app, {get_db: mock_db}):
        response = client.post("/v1/tasks/user-1", json=fake_payload)

    assert response.status_code == 400
    json_response = response.json()
    assert (
        json_response["detail"][0]["message"]
        == f"The task has a type of Unknown Type, which is not allowed."
    )
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
