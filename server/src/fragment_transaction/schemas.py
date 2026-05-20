from src.kit.schemas import Schema


class FragmentTransactionsStats(Schema):
    total_spend: float
    stars_total_spend: float
    premium_total_spend: float


class FragmentTransaction(Schema):
    amount: float
    reason: str
    recipient: str
    recipient_username: str

    stars_amount: int | None
    premium_months: int | None
