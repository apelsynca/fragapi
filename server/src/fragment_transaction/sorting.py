from enum import StrEnum
from typing import Annotated

from fastapi import Depends

from src.kit.sorting import Sorting, SortingGetter


class FragTransactionSortProperty(StrEnum):
    created_at = "created_at"
    amount = "amount"


ListSorting = Annotated[
    list[Sorting[FragTransactionSortProperty]],
    Depends(SortingGetter(FragTransactionSortProperty, ["-created_at"])),
]
