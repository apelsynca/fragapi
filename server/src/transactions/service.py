from sqlalchemy import func

from src.kit.pagination import PaginationParams
from src.models import Transaction, TransactionReason, TransactionStatus, User

from .repository import TransactionRepository
from .schemas import TransactionStats


class TransactionService:
    def __init__(self, repository: TransactionRepository) -> None:
        self.repository = repository

    async def create(
        self,
        amount: float,
        reason: TransactionReason,
        user: User,
        tx_hash: str | None = None,
        stars_quantity: int | None = None,
        recipient: str | None = None,
        status: TransactionStatus = TransactionStatus.PENDING,
    ) -> Transaction:
        return await self.repository.create(
            Transaction(
                amount=amount,
                reason=reason,
                user=user,
                tx_hash=tx_hash,
                stars_quantity=stars_quantity,
                recipient=recipient,
                status=status,
            )
        )

    async def get_by_id(self, transaction_id: int, user: User) -> Transaction | None:
        """Get transaction by ID for a specific user"""
        return await self.repository.get_one_or_none(
            self.repository.get_base_stmt()
            .where(Transaction.id == transaction_id)
            .where(Transaction.user == user)
        )

    async def update_status(
        self, transaction: Transaction, status: TransactionStatus, tx_hash: str | None = None
    ) -> Transaction:
        """Update transaction status and optionally tx_hash"""
        update_data: dict = {"status": status}
        if tx_hash:
            update_data["tx_hash"] = tx_hash
        return await self.repository.update(transaction, update_data)

    async def get_list(
        self, pagination: PaginationParams, user: User
    ) -> tuple[list[Transaction], int]:
        return await self.repository.paginate(
            stmt=self.repository.get_base_stmt()
            .where(Transaction.user == user)
            .order_by(Transaction.created_at.desc()),
            limit=pagination.limit,
            page=pagination.page,
        )

    async def get_stats(self, user: User) -> TransactionStats:
        return await self.repository.get_stats(user)
