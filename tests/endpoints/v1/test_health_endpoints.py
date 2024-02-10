import json
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from plm.endpoints.v1.health import router
from plm.dependencies import get_db_without_user
from tests.dependency_mocker import DependencyMocker

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_healthcheck_ok():
    with DependencyMocker(app, {get_db_without_user: MagicMock()}):
        response = client.get("/v1/healthcheck")

        assert response.status_code == 200
        assert json.loads(response.content) == {"postgres": "OK"}


def test_healthcheck_db_fail():
    mock_get_db_without_user = MagicMock()
    mock_get_db_without_user.execute().fetchall.side_effect = Exception("POP")

    with DependencyMocker(app, {get_db_without_user: mock_get_db_without_user}):
        response = client.get("/v1/healthcheck")

        assert response.status_code == 500
        assert json.loads(response.content) == {
            "postgres": "FAIL",
            "postgres_error": "POP",
        }
