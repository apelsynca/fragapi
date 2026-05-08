from datetime import date

from src.kit.schemas import Schema


class Transaction(Schema):
    pass
    # id: int
    # amount: float
    # reason: TransactionReason
    # status: TransactionStatus
    # message_hash: str | None
    # stars_quantity: int | None
    # recipient: str | None
    # created_at: datetime


class TransactionStats(Schema):
    stars_purchases_count: int  # Количество покупок звезд
    premium_count: int
    total_spent: float


class TransactionChartPoint(Schema):
    date: date
    ton_amount: float
    transactions_count: int
