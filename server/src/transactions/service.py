from sqlalchemy.ext.asyncio import AsyncSession

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
        recipient: str,
        message_hash: str | None = None,
        status: TransactionStatus = TransactionStatus.PENDING,
    ) -> Transaction:
        repository = TransactionRepository.from_session(session)
        return await repository.create(
            Transaction(
                amount=amount,
                reason=reason,
                user=user,
                message_hash=message_hash,
                recipient=recipient,
                status=status,
            )
        )

    async def paginate(
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
        # TODO: MONTHLY
        repository = TransactionRepository.from_session(session)
        return await repository.get_stats(user)


transaction = TransactionService()
