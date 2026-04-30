from datetime import datetime

from src.kit.schemas import Schema


class TelegramAuthData(Schema):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: datetime
    hash: str


class TelegramBotAuthData(Schema):
    hash: str


class LoginResponse(Schema):
    token: str | None
    success: bool
    bot_hash: str | None = None
