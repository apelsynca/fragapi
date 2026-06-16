from typing import Annotated

from pydantic import Field

from src.kit.schemas import DecimalFloat, Schema


class BaseUser(Schema):
    id: Annotated[int, Field(description="The Telegram ID of the user.")]
    first_name: str
    last_name: str | None
    username: str | None


class UserRead(BaseUser):
    balance: DecimalFloat
