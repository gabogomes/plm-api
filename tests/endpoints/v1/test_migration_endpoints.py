from unittest.mock import MagicMock, patch
from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import select, text

from plm.endpoints.v1.migration import router
from plm.security import User
from plm.models import SchemaVersion
from plm.enums import Permission
from plm.dependencies import get_db, get_calling_user, get_settings
from tests.dependency_mocker import DependencyMocker

import json

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_get_versions():
    schema1 = SchemaVersion(
        installed_rank=1,
        version="v1",
        description="d1",
        type="t1",
        script="s1",
        checksum=11,
        installed_by="Neil Armstrong",
        installed_on=datetime(1969, 7, 20),
    )
    schema2 = SchemaVersion(
        installed_rank=2,
        version="v2",
        description="d2",
        type="t2",
        script="s2",
        checksum=21,
        installed_by="Eugene Cernan",
        installed_on=datetime(1972, 12, 11),
    )
    mock_user = User(permissions=[Permission.Admin])
    mock_user.return_value = User(permissions=[Permission.Admin])
    mock_db = MagicMock()
    mock_db.exec.return_value.fetchall.side_effect = [
        [[1]],
        [schema1, schema2],
    ]

    with DependencyMocker(app, {get_db: mock_db, get_calling_user: mock_user}):
        response = client.get("/v1/schema/versions?maxCount=3")

    expected = [
        {
            "installedRank": 1,
            "version": "v1",
            "description": "d1",
            "type": "t1",
            "script": "s1",
            "checksum": 11,
            "installedBy": "Neil Armstrong",
            "installedOn": "1969-07-20T00:00:00",
        },
        {
            "installedRank": 2,
            "version": "v2",
            "description": "d2",
            "type": "t2",
            "script": "s2",
            "checksum": 21,
            "installedBy": "Eugene Cernan",
            "installedOn": "1972-12-11T00:00:00",
        },
    ]
    assert response.status_code == 200
    assert response.json() == expected
    assert mock_db.exec.call_count == 2
    table_query = mock_db.exec.call_args_list[0][0][0]
    expected_table_query = text(
        "select exists(select 1 from information_schema.tables where table_name = 'flyway_schema_history')"
    )
    assert expected_table_query.compare(table_query)
    version_query = mock_db.exec.call_args_list[1][0][0]
    expected_version_query = (
        select(SchemaVersion)
        .distinct()
        .order_by(SchemaVersion.installed_rank.desc())
        .limit(3)
    )
    assert expected_version_query.compare(version_query)


def test_get_versions_no_version_table():
    mock_user = User(permissions=[Permission.Admin])
    mock_db = MagicMock()
    mock_db.exec.return_value.fetchall.return_value = [[0]]

    with DependencyMocker(app, {get_db: mock_db, get_calling_user: mock_user}):
        response = client.get("/v1/schema/versions")

    assert response.status_code == 200
    assert response.json() == []
    assert mock_db.exec.call_count == 1


def test_get_versions_defaults_to_10():
    mock_user = User(permissions=[Permission.Admin])
    mock_user.return_value = User(permissions=[Permission.Admin])
    mock_db = MagicMock()
    mock_db.exec.return_value.fetchall.side_effect = [
        [[1]],
        [],
    ]

    with DependencyMocker(app, {get_db: mock_db, get_calling_user: mock_user}):
        response = client.get("/v1/schema/versions")

    version_query = mock_db.exec.call_args_list[1][0][0]
    expected_version_query = (
        select(SchemaVersion)
        .distinct()
        .order_by(SchemaVersion.installed_rank.desc())
        .limit(10)
    )
    assert expected_version_query.compare(version_query)
