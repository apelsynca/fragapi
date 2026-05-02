from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import ResourceNotFound
from src.kit.pagination import PaginationParams
from src.models import Transaction, TransactionReason, TransactionStatus, User
from src.transactions.repository import TransactionRepository
from src.transactions.schemas import TransactionStats


class TransactionService:
    async def create(
        self,
        session: AsyncSession,
        amount: float,
        reason: TransactionReason,
        user: User,
        tx_hash: str | None = None,
        stars_quantity: int | None = None,
        recipient: str | None = None,
        status: TransactionStatus = TransactionStatus.PENDING,
    ) -> Transaction:
        repository = TransactionRepository.from_session(session)
        return await repository.create(
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

    async def get_by_id(
        self, session: AsyncSession, transaction_id: int, user: User
    ) -> Transaction:
        repository = TransactionRepository.from_session(session)
        transaction = await repository.get_one_or_none(
            repository.get_base_stmt()
            .where(Transaction.id == transaction_id)
            .where(Transaction.user == user)
        )

        if transaction is None:
            raise ResourceNotFound("Transaction not found")

        return transaction

    async def update_status(
        self,
        transaction: Transaction,
        status: TransactionStatus,
        tx_hash: str | None = None,
    ) -> Transaction:
        """Update transaction status and optionally tx_hash"""
        update_data: dict = {"status": status}
        if tx_hash:
            update_data["tx_hash"] = tx_hash
        return await repository.update(transaction, update_data)

    async def get_list(
        self, session: AsyncSession, pagination: PaginationParams, user: User
    ) -> tuple[list[Transaction], int]:
        repository = TransactionRepository.from_session(session)
        stmt = (
            repository.get_base_stmt()
            .where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc())
        )

        return await repository.paginate(
            stmt=stmt,
            limit=pagination.limit,
            page=pagination.page,
        )

    async def get_stats(self, session: AsyncSession, user: User) -> TransactionStats:
        repository = TransactionRepository.from_session(session)
        return await repository.get_stats(user)


transaction = TransactionService()
