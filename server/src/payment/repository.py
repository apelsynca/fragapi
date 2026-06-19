from uuid import UUID

from src.kit.repository import Options
from src.kit.repository.main import BaseRepository
from src.kit.repository.mixins import (
    RepositoryIDMixin,
    RepositorySortingMixin,
    SortingClause,
)
from src.models import Deposit
from src.payment.sorting import PaymentSortProperty


class PaymentRepository(
    RepositorySortingMixin[Deposit, PaymentSortProperty],
    RepositoryIDMixin[Deposit, UUID],
    BaseRepository[Deposit],
):
    model = Deposit

    async def get_by_hash(self, hash: str, *, options: Options = ()):
        stmt = self.get_base_stmt().where(self.model.hash == hash).options(*options)
        return await self.get_one_or_none(stmt=stmt)

    def get_sorting_clause(self, property: PaymentSortProperty) -> SortingClause:
        match property:
            case PaymentSortProperty.created_at:
                return self.model.created_at
