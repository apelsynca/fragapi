from src.kit.schemas import Schema


class TonAPIWebhookMessage(Schema):
    account_id: str
    lt: int  # logical time
    tx_hash: str
