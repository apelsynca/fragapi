import re
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
    photo: str  # backwards compatibility
    name: str
    amount: Annotated[
        float, Field(gt=0, description="Amount that was reduced from your balance")
    ]

    @property
    def avatar_url(self) -> str:
        match = re.search(r'src\s*=\s*"(.+?)"', self.photo)

        if match:
            return match.group(1)

        # NOTE: if i add validator for photo, this could be removed
        return self.photo  # should not happen, fallback
