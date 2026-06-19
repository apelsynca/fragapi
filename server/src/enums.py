from enum import IntEnum, StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class PremiumMonths(IntEnum):
    THREE_MONTHS = 3
    SIX_MONTHS = 6
    YEAR = 12


class RateLimitGroup(StrEnum):
    web = "web"
    default = "default"


class TelegramLogSender(StrEnum):
    logger = "logger"
    chat = "chat"


class TransactionReason(StrEnum):
    premium = "premium"
    stars = "stars"


# WARN: Copy
class FragmentTransactionReason(StrEnum):
    premium = "premium"
    stars = "stars"
