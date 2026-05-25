from enum import StrEnum
from typing import Annotated

from fastapi import Depends

from src.kit.sorting import Sorting, SortingGetter


class GiftModelSortProperty(StrEnum):
    floor = "floor"


ListSorting = Annotated[
    list[Sorting[GiftModelSortProperty]],
    Depends(SortingGetter(GiftModelSortProperty, ["-floor"])),
]
