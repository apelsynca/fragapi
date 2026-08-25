from datetime import datetime

from src.kit.schemas import Schema
from src.models.deposits import DepositStatus
from src.ton_transaction.schemas import TonTransaction


class DepositTonRequestMessage(Schema):
    address: str
    amount: str
    payload: str


class DepositTonMemoResponse(Schema):
    address: str
    amount: float
    memo: str


class BaseDeposit(Schema):
    amount: float
    created_at: datetime
    status: DepositStatus


class Deposit(BaseDeposit):
    ton_transaction: TonTransaction | None
