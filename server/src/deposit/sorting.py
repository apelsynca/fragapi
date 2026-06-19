from enum import StrEnum
from typing import Annotated

from fastapi import Depends

from src.kit.sorting import Sorting, SortingGetter


class DepositSortProperty(StrEnum):
    created_at = "created_at"


ListSorting = Annotated[
    list[Sorting[DepositSortProperty]],
    Depends(SortingGetter(DepositSortProperty, ["-created_at"])),
]
