from datetime import datetime

from src.kit.schemas import Schema
from src.models.deposits import DepositStatus
from src.transaction.schemas import Transaction


class DepositTonRequestMessage(Schema):
    address: str
    amount: str
    payload: str


class BaseDeposit(Schema):
    amount: float
    created_at: datetime
    status: DepositStatus


class Deposit(BaseDeposit):
    transaction: Transaction | None
