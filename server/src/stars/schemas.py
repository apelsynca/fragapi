from src.kit.schemas import Schema


class BuyStars(Schema):
    quantity: int
    username: str
    show_sender: bool = False


class BuyStarsResponse(Schema):
    success: bool
    transaction_hash: str


class StarsRecipient(Schema):
    recipient: str
    photo: str | None
    name: str
