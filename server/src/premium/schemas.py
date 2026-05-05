# class PremiumPriceResponse(Schema):
#     three_months: float
#     six_months: float
#     year: float

from src.enums import PremiumMonths
from src.kit.schemas import Schema
from src.schemas import BaseBuyResponse, BaseRecipient


class BuyPremium(Schema):
    username: str
    months: PremiumMonths


class BuyPremiumResponse(BaseBuyResponse):
    pass


class PremiumRecipient(BaseRecipient):
    pass
