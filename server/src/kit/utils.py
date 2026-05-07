import secrets
from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_api_key() -> str:
    """Create new api token string"""
    return secrets.token_urlsafe(32)
