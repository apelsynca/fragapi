from enum import StrEnum


class Scope(StrEnum):
    web = "web"
    api = "api"

    read_user = "user:read"

    ton_rate_read = "ton_rate:read"
    transactions_read = "transactions:read"

    # for now global stars and premium, also can be stars:buy, premium:gift
    stars = "stars"
    premium = "premium"

    api_tokens_read = "api_tokens:read"

    deposit = "deposit"
