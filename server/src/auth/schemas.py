from src.kit.schemas import Schema


class TelegramBotAuthData(Schema):
    hash: str


class LoginResponse(Schema):
    token: str | None
    success: bool
