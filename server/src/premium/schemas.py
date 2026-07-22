from typing import Annotated

from pydantic import Field

from src.enums import PremiumMonths
from src.schemas import BaseBuyRequest, BaseBuyResponse, BaseRecipient


class BuyPremium(BaseBuyRequest):
    username: Annotated[
        str, Field(description="Telegram username of the user to whom gift Premium")
    ]
    months: PremiumMonths


class BuyPremiumResponse(BaseBuyResponse):
    pass


class PremiumRecipient(BaseRecipient):
    pass
