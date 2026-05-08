from datetime import date

from sqlalchemy import func, select

from src.kit.repository import BaseRepository, IDRepositoryMixin
from src.models import Transaction, TransactionReason, User
from src.models.transactions import TransactionStatus

from .schemas import TransactionStats


class TransactionRepository(
    BaseRepository[Transaction], IDRepositoryMixin[Transaction, int]
):
    model = Transaction

    async def get_stats(self, user: User) -> TransactionStats:
        stmt = select(
            # Количество покупок звезд (count вместо sum)
            func.count()
            .filter(Transaction.reason == TransactionReason.STARS)
            .label("stars_purchases_count"),
            # Количество покупок премиума
            func.count()
            .filter(Transaction.reason == TransactionReason.PREMIUM)
            .label("premium_count"),
            # Общая сумма потраченных средств
            func.coalesce(func.sum(Transaction.amount), 0).label("total_spent"),
        ).where(Transaction.user == user)

        result = await self.session.execute(stmt)
        row = result.one()

        return TransactionStats(
            stars_purchases_count=row.stars_purchases_count,
            premium_count=row.premium_count,
            total_spent=float(row.total_spent),
        )

    def get_chart_data_stmt(self, user: User, start_date: date):
        return (
            select(
                func.date(Transaction.created_at).label("date"),
                func.sum(Transaction.amount).label("ton_amount"),
                func.count().label("transactions_count"),
            )
            .where(
                Transaction.user == user,
                Transaction.status == TransactionStatus.COMPLETED,
                func.date(Transaction.created_at) >= start_date,
            )
            .group_by(func.date(Transaction.created_at))
            .order_by(func.date(Transaction.created_at))
        )
