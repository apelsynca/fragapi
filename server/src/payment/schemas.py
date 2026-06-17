from datetime import datetime

from src.kit.schemas import Schema
from src.models.payments import PaymentStatus


class PaymentTonRequestMessage(Schema):
    address: str
    amount: str
    payload: str


class Payment(Schema):
    amount: float
    created_at: datetime
    status: PaymentStatus
