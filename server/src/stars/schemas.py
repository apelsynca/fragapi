from typing import Annotated

from pydantic import UUID4, Field

from src.enums import BulkPurchaseStatus
from src.kit.schemas import Schema
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


class BulkBuyStars(Schema):
    items: Annotated[
        list[BuyStars],
        Field(
            min_length=1,
            max_length=100,
            description="Purchases to send together in one wallet transaction",
        ),
    ]


class BulkBuyStarsItemResult(Schema):
    username: Annotated[str, Field(description="Username from the request")]
    quantity: Annotated[int, Field(description="Quantity of stars from the request")]
    result: Annotated[
        BuyStarsResponse | None,
        Field(description="The purchase, once this item is bought"),
    ] = None
    error: Annotated[
        str | None, Field(description="Why this item was not bought or charged")
    ] = None


class BulkBuyStarsResponse(Schema):
    id: Annotated[UUID4, Field(description="ID to poll the bulk purchase with")]
    status: Annotated[
        BulkPurchaseStatus,
        Field(description="pending: buying, charged: sending, done: finished"),
    ]
    items: Annotated[
        list[BulkBuyStarsItemResult],
        Field(description="Results in the same order as the requested items"),
    ]
