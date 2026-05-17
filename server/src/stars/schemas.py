from typing import Annotated

from pydantic import UUID4, Field

from src.kit.schemas import Schema
from src.schemas import BaseBuyResponse, BaseRecipient


class BuyStars(Schema):
    username: Annotated[
        str, Field(description="Telegram username of the user to whom buy stars")
    ]
    quantity: Annotated[
        int, Field(ge=50, le=10_000_000, description="Quantity of stars to buy")
    ]


class StarsRecipient(BaseRecipient):
    pass


class BuyStarsResponse(BaseBuyResponse):
    transaction_id: UUID4
    photo: str
    name: str
    amount: Annotated[
        float, Field(gt=0, description="Amount that was reduced from your balance")
    ]
