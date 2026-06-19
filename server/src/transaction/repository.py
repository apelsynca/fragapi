from uuid import UUID

from src.kit.repository.main import BaseRepository
from src.kit.repository.mixins import (
    RepositoryIDMixin,
    RepositorySortingMixin,
    SortingClause,
)
from src.models import Transaction
from src.transaction.sorting import FragTransactionSortProperty


class FragmentTransactionRepository(
    BaseRepository[Transaction],
    RepositoryIDMixin[Transaction, UUID],
    RepositorySortingMixin[Transaction, FragTransactionSortProperty],
):
    model = Transaction

    def get_sorting_clause(
        self, property: FragTransactionSortProperty
    ) -> SortingClause:
        match property:
            case FragTransactionSortProperty.created_at:
                return Transaction.created_at
            case FragTransactionSortProperty.amount:
                return Transaction.amount
