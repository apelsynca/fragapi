from sqlalchemy import func, select

from src.kit.repository.id_mixin import IDRepositoryMixin
from src.kit.repository.main import BaseRepository
from src.models import Transaction, TransactionReason, User

from .schemas import TransactionStats


class TransactionRepository(
    BaseRepository[Transaction], IDRepositoryMixin[Transaction, int]
):
    model = Transaction

    async def get_stats(self, user: User) -> TransactionStats:
        stmt = select(
            # Количество покупок звезд (count вместо sum)
            func.count().filter(
                Transaction.reason == TransactionReason.STARS
            ).label("stars_purchases_count"),
            # Количество покупок премиума
            func.count().filter(
                Transaction.reason == TransactionReason.PREMIUM
            ).label("premium_count"),
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
