from typing import Annotated

from pydantic import Field

from src.schemas import (
    BaseBuyRequest,
    BaseBuyResponse,
    BaseRecipient,
    TelegramUsername,
)


class BuyStars(BaseBuyRequest):
    username: Annotated[
        TelegramUsername,
        Field(description="Telegram username of the user to whom buy stars"),
    ]
    quantity: Annotated[
        int, Field(ge=50, le=10_000_000, description="Quantity of stars to buy")
    ]


class StarsRecipient(BaseRecipient):
    pass


class BuyStarsResponse(BaseBuyResponse):
    pass
