import math
from collections.abc import Sequence
from typing import Annotated, NamedTuple, Self

from fastapi import Depends, Query
from pydantic import BaseModel

from src.config import settings
from src.kit.schemas import Schema


class PaginationParams(NamedTuple):
    page: int
    limit: int


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
