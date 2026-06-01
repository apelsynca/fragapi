from enum import StrEnum


class Scope(StrEnum):
    web = "web"
    api = "api"
    admin = "admin"

    read_user = "user:read"

    ton_rate_read = "ton_rate:read"
    transactions_read = "transactions:read"

    # for now global stars and premium, also can be stars:buy, premium:gift
    stars = "stars"
    premium = "premium"

    read_api_keys = "read_api_keys"
    api_tokens_read = "api_tokens:read"
