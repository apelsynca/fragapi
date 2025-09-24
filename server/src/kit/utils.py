import secrets
from datetime import UTC, datetime

from src.enums import TON_FEE


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_api_key() -> str:
    """Create new api token string"""
    return secrets.token_urlsafe(48)


def after_fee(amount: float) -> float:
    """Calculate amount with TON blockchain fee's"""
    return amount * (1 + TON_FEE)
