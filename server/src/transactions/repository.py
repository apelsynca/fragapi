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
            func.coalesce(
                func.sum(Transaction.amount).filter(
                    Transaction.reason == TransactionReason.STARS
                ),
                0,
            ).label("stars_count"),
            func.count().filter(Transaction.reason == TransactionReason.PREMIUM).label(
                "premium_count"
            ),
            func.coalesce(func.sum(Transaction.amount), 0).label("total_spent"),
        ).where(Transaction.user == user)

        result = await self.session.execute(stmt)
        row = result.one()

        return TransactionStats(
            stars_count=int(row.stars_count),
            premium_count=row.premium_count,
            total_spent=float(row.total_spent),
        )
