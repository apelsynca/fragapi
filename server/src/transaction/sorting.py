from enum import StrEnum
from typing import Annotated

from fastapi import Depends

from src.kit.sorting import Sorting, SortingGetter


class TransactionSortProperty(StrEnum):
    created_at = "created_at"
    amount = "amount"


ListSorting = Annotated[
    list[Sorting[TransactionSortProperty]],
    Depends(SortingGetter(TransactionSortProperty, ["-created_at"])),
]
