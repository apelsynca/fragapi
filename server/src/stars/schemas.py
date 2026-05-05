from typing import Annotated

from pydantic import Field

from src.kit.schemas import Schema
from src.schemas import BaseBuyResponse, BaseRecipient


class StarsRecipient(BaseRecipient):
    pass


class BuyStarsResponse(BaseBuyResponse):
    pass


class BuyStars(Schema):
    quantity: Annotated[int, Field(ge=50, le=10_000_000)]
    username: str
