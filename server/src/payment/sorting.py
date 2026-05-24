from enum import StrEnum
from typing import Annotated

from fastapi import Depends

from src.kit.sorting import Sorting, SortingGetter


class PaymentSortProperty(StrEnum):
    created_at = "created_at"


ListSorting = Annotated[
    list[Sorting[PaymentSortProperty]],
    Depends(SortingGetter(PaymentSortProperty, ["-created_at"])),
]
