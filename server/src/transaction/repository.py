from uuid import UUID

from src.kit.repository.main import BaseRepository
from src.kit.repository.mixins import (
    RepositoryIDMixin,
    RepositorySortingMixin,
    SortingClause,
)
from src.models import Transaction
from src.transaction.sorting import TransactionSortProperty


class TransactionRepository(
    BaseRepository[Transaction],
    RepositoryIDMixin[Transaction, UUID],
    RepositorySortingMixin[Transaction, TransactionSortProperty],
):
    model = Transaction

    def get_sorting_clause(self, property: TransactionSortProperty) -> SortingClause:
        match property:
            case TransactionSortProperty.created_at:
                return Transaction.created_at
            case TransactionSortProperty.amount:
                return Transaction.amount
