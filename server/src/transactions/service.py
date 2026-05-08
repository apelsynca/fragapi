from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.kit.pagination import PaginationParams
from src.kit.utils import utc_now
from src.models import Transaction, TransactionReason, TransactionStatus, User
from src.transactions.repository import TransactionRepository
from src.transactions.schemas import TransactionChartPoint, TransactionStats


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

    async def get_chart_stats(
        self, session: AsyncSession, user: User
    ) -> list[TransactionChartPoint]:
        days_count = 90

        end_date = utc_now().date()
        start_date = end_date - timedelta(days=days_count - 1)

        repository = TransactionRepository.from_session(session)
        stmt = repository.get_chart_data_stmt(user=user, start_date=start_date)

        result = await session.execute(stmt)
        rows = result.all()

        validated = [
            TransactionChartPoint(
                date=row.date,
                ton_amount=row.ton_amount,
                transactions_count=row.transactions_count,
            )
            for row in rows
        ]

        non_empty_dates = {ch_st.date: ch_st for ch_st in validated}

        full_stats: list[TransactionChartPoint] = []
        for i in range(days_count):
            day = start_date + timedelta(days=i)
            full_stats.append(
                non_empty_dates.get(
                    day,
                    TransactionChartPoint(date=day, ton_amount=0, transactions_count=0),
                ),
            )

        return full_stats


transaction = TransactionService()
