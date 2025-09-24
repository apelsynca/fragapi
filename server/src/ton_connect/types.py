from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class TonConnectMessage(BaseModel):
    address: str
    amount: int
    payload: str | None = None


class TonConnectTransaction(BaseModel):
    valid_until: Annotated[datetime, Field(alias="validUntil")]
    from_address: Annotated[str, Field(alias="from")]
    messages: list[TonConnectMessage]
