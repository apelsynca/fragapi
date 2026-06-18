from datetime import datetime

from src.kit.schemas import Schema
from src.models.payments import PaymentStatus
from src.transaction.schemas import Transaction


class PaymentTonRequestMessage(Schema):
    address: str
    amount: str
    payload: str


class BasePayment(Schema):
    amount: float
    created_at: datetime
    status: PaymentStatus


class Payment(BasePayment):
    transaction: Transaction | None
