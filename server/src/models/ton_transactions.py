from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .deposits import Deposit
    from .transactions import Transaction


class TonTransaction(RecordModel):
    """Dont confuze with Transaction model (prev FragmentTransaction)"""

    __tablename__ = "ton_transactions"
    __table_args__ = (
        # Deposits have no message hash: one incoming chain transaction, one row.
        # Purchases sent together in one wallet message share the chain hash.
        Index(
            "uq_ton_transactions_deposit_hash",
            "hash",
            unique=True,
            postgresql_where=text("message_hash IS NULL"),
        ),
    )

    # nano tons transaction amount
    nano_amount: Mapped[int] = mapped_column(BigInteger)

    hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True, default=None
    )
    message_hash: Mapped[str] = mapped_column(
        String(64), nullable=True, index=True, unique=True
    )

    from_address: Mapped[str] = mapped_column(String(100))  # workchain:init
    to_address: Mapped[str] = mapped_column(String(100))  # workchain:init

    deposit: Mapped["Deposit | None"] = relationship(
        back_populates="ton_transaction", uselist=False, lazy="raise"
    )
    transaction: Mapped["Transaction | None"] = relationship(
        back_populates="ton_transaction", uselist=False, lazy="raise"
    )
