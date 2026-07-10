from datetime import date

from src.kit.schemas import Schema, TimestampedSchema
from src.ton_transaction.schemas import TonTransaction


class TransactionStats(Schema):
    total_spend: float
    stars_total_spend: float
    premium_total_spend: float


class BaseTransaction(TimestampedSchema):
    amount: float
    reason: str
    recipient: str
    recipient_username: str


class Transaction(BaseTransaction):
    stars_amount: int | None
    premium_months: int | None

    ton_transaction: TonTransaction


class ChartPoint(Schema):
    date: date
    stars_spend: float
    premium_spend: float
