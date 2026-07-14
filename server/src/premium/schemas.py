from typing import Annotated

from pydantic import Field, field_validator

from src.enums import PremiumMonths
from src.kit.schemas import Schema
from src.schemas import BaseBuyResponse, BaseRecipient


class BuyPremium(Schema):
    username: Annotated[
        str, Field(description="Telegram username of the user to whom gift Premium")
    ]
    months: PremiumMonths

    @field_validator("username", mode="before")
    @classmethod
    def strip_telegram_prefix(cls, v: str) -> str:
        return v.removeprefix("https://t.me/").removeprefix("https://telegram.me")


class BuyPremiumResponse(BaseBuyResponse):
    pass


class PremiumRecipient(BaseRecipient):
    pass
