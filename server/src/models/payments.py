from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .transactions import Transaction
    from .users import User


class Payment(RecordModel):
    __tablename__ = "payments"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", lazy="joined")

    # amount just as amount
    amount: Mapped[float]
    hash: Mapped[str] = mapped_column(unique=True)

    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("transactions.id"), unique=True
    )
    transaction: Mapped["Transaction | None"] = relationship(
        back_populates="payment", uselist=False
    )
