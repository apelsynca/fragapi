from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .users import User


# rename this to lowercase
class TransactionReason(StrEnum):
    PREMIUM = "PREMIUM"
    STARS = "STARS"


# rename this to lowercase
class TransactionStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Transaction(RecordModel):
    amount: Mapped[float]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="transactions")

    reason: Mapped[TransactionReason] = mapped_column(
        Enum(TransactionReason, native_enum=False)
    )
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, native_enum=False),
        default=TransactionStatus.PENDING,
    )

    # in theory we could know the message_hash even before sending
    message_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )

    recipient: Mapped[str] = mapped_column(String(255))
