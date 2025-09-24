from src.kit.pagination import PaginationParams
from src.models import Transaction, TransactionReason, User

from .repository import TransactionRepository


class TransactionService:
    def __init__(self, repository: TransactionRepository) -> None:
        self.repository = repository

    async def create(
        self, amount: float, reason: TransactionReason, user: User
    ) -> Transaction:
        return await self.repository.create(
            Transaction(amount=amount, reason=reason, user=user)
        )

    async def get_list(
        self, pagination: PaginationParams, user: User
    ) -> tuple[list[Transaction], int]:
        return await self.repository.paginate(
            stmt=self.repository.get_base_stmt().where(Transaction.user == user),
            limit=pagination.limit,
            page=pagination.page,
        )
