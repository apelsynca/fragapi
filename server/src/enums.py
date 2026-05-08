from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class PremiumMonths(StrEnum):
    THREE_MONTHS = "3"
    SIX_MONTHS = "6"
    YEAR = "12"
