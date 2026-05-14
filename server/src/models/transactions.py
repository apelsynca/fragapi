from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .fragment_transactions import FragmentTransaction
    from .payments import Payment


class Transaction(RecordModel):
    __tablename__ = "transactions"

    # nano tons transaction amount
    nano_amount: Mapped[int]

    hash: Mapped[str] = mapped_column(
        String(64), nullable=True, index=True, unique=True
    )
    # in theory we could know the message_hash even before sending
    message_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True, unique=True
    )

    from_wallet: Mapped[str] = mapped_column(String(100))  # workchain:init
    to_wallet: Mapped[str] = mapped_column(String(100))  # workchain:init

    payment: Mapped["Payment | None"] = relationship(
        back_populates="transaction", uselist=False, lazy="raise"
    )
    fragment_transaction: Mapped["FragmentTransaction | None"] = relationship(
        back_populates="transaction", uselist=False, lazy="raise"
    )

    __table_args__ = (
        CheckConstraint(
            "(hash IS NOT NULL) OR (message_hash IS NOT NULL)", name="not_both_null"
        ),
    )
