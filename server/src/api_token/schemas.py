from datetime import datetime

from src.kit.schemas import Schema


class ApiTokenCreate(Schema):
    name: str
    expires_at: datetime | None = None
