from datetime import datetime

from pydantic import BaseModel


class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    photo_url: str | None = None
    auth_date: datetime
    hash: str


class TelegramBotAuthData(BaseModel):
    hash: str


class LoginResponse(BaseModel):
    token: str | None
    success: bool
    bot_hash: str | None = None
