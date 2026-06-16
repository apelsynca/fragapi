from typing import Literal

from pydantic import BaseModel


# needs to be BaseModel
class TonAPIWebhookMessage(BaseModel):
    event_type: str | Literal["account_tx"]
    account_id: str
    lt: int  # logical time
    tx_hash: str  # blockchain transaction hash
