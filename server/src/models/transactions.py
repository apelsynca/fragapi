from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .deposits import Deposit
    from .fragment_transactions import FragmentTransaction


class Transaction(RecordModel):
    __tablename__ = "transactions"

    # nano tons transaction amount
    nano_amount: Mapped[int] = mapped_column(BigInteger)

    hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True, unique=True, default=None
    )
    message_hash: Mapped[str] = mapped_column(
        String(64), nullable=True, index=True, unique=True
    )

    from_address: Mapped[str] = mapped_column(String(100))  # workchain:init
    to_address: Mapped[str] = mapped_column(String(100))  # workchain:init

    deposit: Mapped["Deposit | None"] = relationship(
        back_populates="transaction", uselist=False, lazy="raise"
    )
    fragment_transaction: Mapped["FragmentTransaction | None"] = relationship(
        back_populates="transaction", uselist=False, lazy="raise"
    )
