from datetime import datetime

from src.kit.schemas import IDSchema, Schema


class ApiTokenCreate(Schema):
    name: str
    expires_at: datetime | None = None


class ApiToken(IDSchema):
    name: str
    token: str
    expires_at: datetime | None
    last_used_at: datetime | None
