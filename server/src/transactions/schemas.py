from datetime import datetime

from src.kit.schemas import Schema
from src.models.transactions import TransactionReason


class Transaction(Schema):
    amount: float
    reason: TransactionReason
    created_at: datetime


class TransactionStats(Schema):
    stars_count: int
    premium_count: int
    total_spent: float
