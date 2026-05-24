from src.kit.schemas import Schema


class PaymentTonRequestMessage(Schema):
    address: str
    amount: str
    payload: str


class Payment(Schema):
    pass
