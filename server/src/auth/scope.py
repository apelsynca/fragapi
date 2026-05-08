from enum import StrEnum


class Scope(StrEnum):
    web = "web"
    api = "api"
    admin = "admin"

    transactions_read = "transactions:read"
