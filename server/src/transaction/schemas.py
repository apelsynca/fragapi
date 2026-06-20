from datetime import date

from src.kit.schemas import Schema, TimestampedSchema


class TransactionStats(Schema):
    total_spend: float
    stars_total_spend: float
    premium_total_spend: float


class Transaction(TimestampedSchema):
    amount: float
    reason: str
    recipient: str
    recipient_username: str

    stars_amount: int | None
    premium_months: int | None


class ChartPoint(Schema):
    date: date
    stars_spend: float
    premium_spend: float
