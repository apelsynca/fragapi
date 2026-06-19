from datetime import datetime

from src.kit.schemas import Schema
from src.models.deposits import DepositStatus
from src.transaction.schemas import Transaction


class PaymentTonRequestMessage(Schema):
    address: str
    amount: str
    payload: str


class BasePayment(Schema):
    amount: float
    created_at: datetime
    status: DepositStatus


class Payment(BasePayment):
    transaction: Transaction | None
