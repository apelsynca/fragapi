from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class TonConnectMessage(BaseModel):
    address: str
    amount: int
    payload: str | None = None


class TonConnectTransaction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    valid_until: Annotated[datetime, Field(alias="validUntil")]
    from_address: Annotated[str, Field(alias="from")]
    messages: list[TonConnectMessage]


class TonAPIWebhookMessage(BaseModel):
    account_id: str
    lt: int  # logical time
    tx_hash: str  # blockchain transaction hash
