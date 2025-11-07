from src.fragment.enums import PremiumMonths
from src.kit.schemas import Schema


class BuyPremium(Schema):
    username: str
    months: PremiumMonths


class BuyPremiumResponse(Schema):
    success: bool
    transaction_hash: str


class PremiumRecipient(Schema):
    recipient: str
    photo: str | None
    name: str
