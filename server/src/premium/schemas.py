# from src.fragment_rest.enums import PremiumMonths
# from src.kit.schemas import Schema
#
#
#
# class PremiumPriceResponse(Schema):
#     three_months: float
#     six_months: float
#     year: float

from src.enums import PremiumMonths
from src.kit.schemas import Schema
from src.schemas import BaseRecipient


class BuyPremium(Schema):
    username: str
    months: PremiumMonths


class BuyPremiumResponse(Schema):
    transaction_hash: str


class PremiumRecipient(BaseRecipient):
    pass
