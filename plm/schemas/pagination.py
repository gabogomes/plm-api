from typing import TypeVar, Generic

from fastapi import Query

from fastapi_pagination.limit_offset import (
    LimitOffsetPage as BasePage,
    LimitOffsetParams as BaseParams,
)

T = TypeVar("T")


class Params(BaseParams):
    limit: int = Query(50, ge=1, le=1_000, description="Limit")


class Page(BasePage[T], Generic[T]):
    __params_type__ = Params
