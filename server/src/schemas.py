import re
from typing import Annotated

from pydantic import UUID4, Field, computed_field, field_validator

from src.kit.schemas import Schema


class BaseRecipient(Schema):
    recipient: str
    photo: str
    name: str

    @computed_field
    @property
    def avatar_url(self) -> str:
        return extract_photo(photo_tag=self.photo)


class BaseBuyRequest(Schema):
    username: str
    show_sender: Annotated[
        bool, Field(default=False, description="Show telegram sender")
    ]

    @field_validator("username", mode="before")
    @classmethod
    def strip_telegram_prefix(cls, v: str) -> str:
        return v.removeprefix("https://t.me/")


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
