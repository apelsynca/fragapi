import re
from typing import Annotated

from pydantic import UUID4, BeforeValidator, Field, computed_field

from src.kit.schemas import Schema


def strip_telegram_prefix(v: str) -> str:
    return (
        v.removeprefix("https://t.me/").removeprefix("https://telegram.me/").lstrip("@")
    )


TelegramUsername = Annotated[
    str,
    BeforeValidator(strip_telegram_prefix),
    # the docs prefill requests with the example, so it must be a real account
    Field(examples=["synca"]),
]


class BaseBuyRequest(Schema):
    username: TelegramUsername
    show_sender: bool = Field(default=False, description="Show telegram sender")


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
