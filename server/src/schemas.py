from src.kit.schemas import Schema


class BaseRecipient(Schema):
    recipient: str
    photo: str
    name: str


class BaseBuyResponse(Schema):
    message_hash: str
