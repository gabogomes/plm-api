import pytest
from fastapi import HTTPException

from plm.services.validation_exceptions import raise_validation_exception


def test_raise_single_error():
    with pytest.raises(HTTPException) as excinfo:
        raise_validation_exception("pop")

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == [{"message": "pop"}]


def test_raise_multiple_errors():
    with pytest.raises(HTTPException) as excinfo:
        raise_validation_exception(
            ["message error 1", "message error 2", "message error 3"]
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == [
        {"message": "message error 1"},
        {"message": "message error 2"},
        {"message": "message error 3"},
    ]


def test_raise_error_with_single_property():
    with pytest.raises(HTTPException) as excinfo:
        raise_validation_exception("message body 1", "message prop 1")

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == [
        {"message": "message body 1", "properties": ["message prop 1"]}
    ]


def test_raise_error_with_multiple_properties():
    with pytest.raises(HTTPException) as excinfo:
        raise_validation_exception(
            "message body 1", ["message prop 1", "message prop 2"]
        )

    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == [
        {
            "message": "message body 1",
            "properties": ["message prop 1", "message prop 2"],
        }
    ]
