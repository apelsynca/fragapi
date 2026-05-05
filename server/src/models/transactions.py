from enum import StrEnum, auto
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .users import User


class TransactionReason(StrEnum):
    PREMIUM = auto()
    STARS = auto()


class TransactionStatus(StrEnum):
    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()


class Transaction(RecordModel):
    amount: Mapped[float]

    reason: Mapped[TransactionReason] = mapped_column(
        Enum(TransactionReason, native_enum=False)
    )
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, native_enum=False),
        default=TransactionStatus.PENDING,
    )

    message_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )

    recipient: Mapped[str] = mapped_column(String(255))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User")
