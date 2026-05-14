from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .transactions import Transaction
    from .users import User


class FragmentTransactionReason(StrEnum):
    premium = "premium"
    stars = "stars"


class FragmentTransaction(RecordModel):
    __tablename__ = "fragment_transactions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="fragment_transactions")

    # amount with fee
    amount: Mapped[float]

    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("transactions.id"), unique=True
    )
    transaction: Mapped["Transaction"] = relationship(
        "Transaction", back_populates="fragment_transaction"
    )

    reason: Mapped[FragmentTransactionReason] = mapped_column(
        Enum(FragmentTransactionReason, native_enum=False)
    )
