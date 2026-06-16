import re
from typing import Annotated

from pydantic import UUID4, Field, computed_field

from src.kit.schemas import DecimalFloat, Schema


class BaseRecipient(Schema):
    recipient: str
    photo: str
    name: str

    @computed_field
    @property
    def avatar_url(self) -> str:
        match = re.search(r'src\s*=\s*"(.+?)"', self.photo)

        if match:
            return match.group(1)

        # NOTE: fallback, but if i add validator for photo, this could be removed
        return self.photo


class BaseBuyResponse(Schema):
    message_hash: str
    transaction_id: UUID4
    photo: str  # backwards compatibility
    name: str
    amount: Annotated[
        DecimalFloat,
        Field(gt=0, description="Amount that was reduced from your balance"),
    ]

    @computed_field
    @property
    def avatar_url(self) -> str:
        match = re.search(r'src\s*=\s*"(.+?)"', self.photo)

        if match:
            return match.group(1)

        # NOTE: fallback, but if i add validator for photo, this could be removed
        return self.photo
