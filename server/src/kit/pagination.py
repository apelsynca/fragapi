import math
from collections.abc import Sequence
from typing import Annotated, Any, NamedTuple, Self

from fastapi import Depends, Query
from pydantic import BaseModel
from sqlalchemy import Select, Subquery, literal

from src.config import settings
from src.kit.schemas import Schema


class PaginationParams(NamedTuple):
    page: int
    limit: int


def count_subquery(statement: Select[Any]) -> Subquery:
    """Build a count-safe subquery from a Select.

    `.subquery()` materializes every mapped column of the underlying entity,
    including those marked `deferred=True`. For count queries we only need
    row cardinality, so project a literal to avoid referencing (or loading)
    unused columns.
    """
    return statement.with_only_columns(literal(1)).order_by(None).subquery()


def get_pagination_params(
    page: int = Query(default=1, description="Page number, defaults to 1."),
    limit: int = Query(
        default=10,
        description=(
            "Limit of items in a page, defaults to 10. "
            f"Maximum is {settings.API_PAGINATION_MAX_LIMIT}."
        ),
        gt=0,
    ),
) -> PaginationParams:
    return PaginationParams(
        page=page,
        limit=min(settings.API_PAGINATION_MAX_LIMIT, limit),
    )


PaginationParamsQuery = Annotated[PaginationParams, Depends(get_pagination_params)]


class Pagination(Schema):
    total_count: int
    max_page: int


class ListResource[T](BaseModel):
    items: list[T]
    pagination: Pagination

    @classmethod
    def from_paginated_results(
        cls, items: Sequence[T], total_count: int, pagination_params: PaginationParams
    ) -> Self:
        return cls(
            items=list(items),
            pagination=Pagination(
                total_count=total_count,
                max_page=math.ceil(total_count / pagination_params.limit),
            ),
        )
