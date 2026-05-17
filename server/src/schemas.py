from typing import Annotated

from pydantic import UUID4, Field

from src.kit.schemas import Schema


class BaseRecipient(Schema):
    recipient: str
    photo: str
    name: str


class BaseBuyResponse(Schema):
    message_hash: str
    transaction_id: UUID4
    photo: str
    name: str
    amount: Annotated[
        float, Field(gt=0, description="Amount that was reduced from your balance")
    ]
