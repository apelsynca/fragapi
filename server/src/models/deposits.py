from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .ton_transactions import TonTransaction
    from .users import User


class DepositStatus(StrEnum):
    pending = "pending"
    failed = "failed"
    completed = "completed"


class Deposit(RecordModel):
    __tablename__ = "deposits"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", lazy="joined")

    # amount just as amount
    amount: Mapped[float]
    # it is just prettier to be like that
    hash: Mapped[str] = mapped_column(unique=True)

    ton_transaction_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ton_transactions.id"), unique=True
    )
    ton_transaction: Mapped["TonTransaction | None"] = relationship(
        back_populates="deposit", uselist=False
    )

    # not sure about that
    status: Mapped[DepositStatus] = mapped_column(
        Enum(DepositStatus, native_enum=False), default=DepositStatus.pending
    )

    # can add paid_at here
