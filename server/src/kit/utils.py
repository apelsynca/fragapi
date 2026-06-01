import secrets
import uuid
from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


def generate_api_token() -> str:
    """Create new api token string"""
    return secrets.token_urlsafe(32)
