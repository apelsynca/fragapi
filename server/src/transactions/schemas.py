from datetime import datetime

from src.kit.schemas import Schema
from src.models.transactions import TransactionReason, TransactionStatus


class Transaction(Schema):
    id: int
    amount: float
    reason: TransactionReason
    status: TransactionStatus
    message_hash: str | None
    stars_quantity: int | None
    recipient: str | None
    created_at: datetime


class TransactionStats(Schema):
    stars_purchases_count: int  # Количество покупок звезд
    premium_count: int
    total_spent: float
