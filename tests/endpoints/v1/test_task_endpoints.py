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
