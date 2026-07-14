from typing import Annotated

from pydantic import Field, field_validator

from src.kit.schemas import Schema
from src.schemas import BaseBuyResponse, BaseRecipient


class BuyStars(Schema):
    username: Annotated[
        str, Field(description="Telegram username of the user to whom buy stars")
    ]
    quantity: Annotated[
        int, Field(ge=50, le=10_000_000, description="Quantity of stars to buy")
    ]

    @field_validator("username", mode="before")
    @classmethod
    def strip_telegram_prefix(cls, v: str) -> str:
        return v.removeprefix("https://t.me/").removeprefix("https://telegram.me")


class StarsRecipient(BaseRecipient):
    pass


class BuyStarsResponse(BaseBuyResponse):
    pass
