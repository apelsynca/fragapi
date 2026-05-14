from uuid import UUID

from src.kit.repository import BaseRepository, IDRepositoryMixin
from src.models import Transaction


class TransactionRepository(
    BaseRepository[Transaction], IDRepositoryMixin[Transaction, UUID]
):
    model = Transaction

    # async def get_stats(self, user: User) -> tuple[int, int, float]:
    #     stmt = select(
    #         # Количество покупок звезд (count вместо sum)
    #         func.count()
    #         .filter(Transaction.reason == TransactionReason.stars)
    #         .label("stars_purchases_count"),
    #         # Количество покупок премиума
    #         func.count()
    #         .filter(Transaction.reason == TransactionReason.premium)
    #         .label("premium_count"),
    #         # Общая сумма потраченных средств
    #         func.coalesce(func.sum(Transaction.amount), 0).label("total_spent"),
    #     ).where(Transaction.user == user)
    #
    #     result = await self.session.execute(stmt)
    #     row = result.one()
    #
    #     return (row.stars_purchases_count, row.premium_count, float(row.total_spent))
    #
    # def get_monthly_stmt(self, user: User) -> Select[tuple[float, float, float]]:
    #     now = utc_now()
    #     start_of_the_month = now - timedelta(days=30)
    #
    #     return select(
    #         func.sum(Transaction.amount).label("monthly_spend"),
    #         func.sum(Transaction.amount)
    #         .filter(Transaction.reason == TransactionReason.stars)
    #         .label("stars_monthly_spend"),
    #         func.sum(Transaction.amount)
    #         .filter(Transaction.reason == TransactionReason.premium)
    #         .label("premium_monthly_spend"),
    #     ).where(Transaction.created_at >= start_of_the_month, Transaction.user == user)
    #
    # def get_chart_data_stmt(self, user: User, start_date: date):
    #     return (
    #         select(
    #             func.date(Transaction.created_at).label("date"),
    #             func.sum(Transaction.amount).label("ton_amount"),
    #             func.count().label("transactions_count"),
    #         )
    #         .where(
    #             Transaction.user == user,
    #             Transaction.status == TransactionStatus.completed,
    #             func.date(Transaction.created_at) >= start_date,
    #         )
    #         .group_by(func.date(Transaction.created_at))
    #         .order_by(func.date(Transaction.created_at))
    #     )
