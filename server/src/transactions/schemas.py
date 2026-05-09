from datetime import date, datetime

from src.kit.schemas import Schema
from src.models.transactions import TransactionReason, TransactionStatus


class Transaction(Schema):
    amount: float
    reason: TransactionReason
    status: TransactionStatus
    message_hash: str | None
    recipient: str
    created_at: datetime


class TransactionStats(Schema):
    stars_purchases_count: int  # Количество покупок звезд
    premium_count: int
    total_spent: float


class TransactionChartPoint(Schema):
    date: date
    ton_amount: float
    transactions_count: int
