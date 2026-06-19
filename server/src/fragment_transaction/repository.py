from uuid import UUID

from src.fragment_transaction.sorting import FragTransactionSortProperty
from src.kit.repository.main import BaseRepository
from src.kit.repository.mixins import (
    RepositoryIDMixin,
    RepositorySortingMixin,
    SortingClause,
)
from src.models import FragmentTransaction


class FragmentTransactionRepository(
    BaseRepository[FragmentTransaction],
    RepositoryIDMixin[FragmentTransaction, UUID],
    RepositorySortingMixin[FragmentTransaction, FragTransactionSortProperty],
):
    model = FragmentTransaction

    def get_sorting_clause(
        self, property: FragTransactionSortProperty
    ) -> SortingClause:
        match property:
            case FragTransactionSortProperty.created_at:
                return FragmentTransaction.created_at
            case FragTransactionSortProperty.amount:
                return FragmentTransaction.amount
