import re
from typing import Annotated

from pydantic import UUID4, Field, computed_field

from src.kit.schemas import Schema


class BaseRecipient(Schema):
    recipient: str
    photo: str
    name: str

    @computed_field
    @property
    def avatar_url(self) -> str:
        return extract_photo(photo_tag=self.photo)


class BaseBuyResponse(Schema):
    message_hash: str
    transaction_id: UUID4
    photo: str  # backwards compatibility
    name: str
    amount: Annotated[
        float, Field(gt=0, description="Amount that was reduced from your balance")
    ]

    @computed_field
    @property
    def avatar_url(self) -> str:
        return extract_photo(photo_tag=self.photo)


def extract_photo(photo_tag: str) -> str:
    match = re.search(r'src\s*=\s*"(.+?)"', photo_tag)
    if match:
        return match.group(1)
    return photo_tag
