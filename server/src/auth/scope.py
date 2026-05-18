from enum import StrEnum


class Scope(StrEnum):
    web = "web"
    api = "api"
    admin = "admin"

    ton_rate_read = "ton_rate:read"
    transactions_read = "transactions:read"

    # for now global stars and premium, also can be stars:buy, premium:gift
    stars = "stars"
    premium = "premium"
