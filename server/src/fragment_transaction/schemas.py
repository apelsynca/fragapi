from datetime import date

from src.kit.schemas import DecimalFloat, Schema, TimestampedSchema


class FragmentTransactionsStats(Schema):
    total_spend: DecimalFloat
    stars_total_spend: DecimalFloat
    premium_total_spend: DecimalFloat


class FragmentTransaction(TimestampedSchema):
    amount: DecimalFloat
    reason: str
    recipient: str
    recipient_username: str

    stars_amount: int | None = None
    premium_months: int | None = None


class ChartPoint(Schema):
    date: date
    stars_spend: DecimalFloat
    premium_spend: DecimalFloat
