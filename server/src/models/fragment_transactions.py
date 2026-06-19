from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .ton_transactions import TonTransaction
    from .users import User


class FragmentTransactionReason(StrEnum):
    premium = "premium"
    stars = "stars"


class FragmentTransaction(RecordModel):
    __tablename__ = "fragment_transactions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="fragment_transactions")

    amount: Mapped[float]  # amount in TON with fee
    recipient: Mapped[str]  # later can be nullable
    recipient_username: Mapped[str]  # later can be nullable

    ton_transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("ton_transactions.id"), unique=True
    )
    ton_transaction: Mapped["TonTransaction"] = relationship(
        back_populates="fragment_transaction"
    )

    reason: Mapped[FragmentTransactionReason] = mapped_column(
        Enum(FragmentTransactionReason, native_enum=False)
    )

    stars_amount: Mapped[int | None]
    premium_months: Mapped[int | None]
