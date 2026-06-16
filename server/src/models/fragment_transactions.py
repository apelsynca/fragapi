from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Numeric
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

    amount: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=9))  # amount in TON with fee
    recipient: Mapped[str]  # later can be nullable
    recipient_username: Mapped[str]  # later can be nullable

    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("transactions.id"), unique=True
    )
    transaction: Mapped["Transaction"] = relationship(
        "Transaction", back_populates="fragment_transaction"
    )

    reason: Mapped[FragmentTransactionReason] = mapped_column(
        Enum(FragmentTransactionReason, native_enum=False)
    )

    stars_amount: Mapped[int | None]
    premium_months: Mapped[int | None]
