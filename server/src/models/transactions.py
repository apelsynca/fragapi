from enum import StrEnum, auto
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.models import RecordModel

if TYPE_CHECKING:
    from .users import User


class TransactionReason(StrEnum):
    PREMIUM = auto()
    STARS = auto()


class Transaction(RecordModel):
    amount: Mapped[float]
    reason: Mapped[TransactionReason] = mapped_column(
        Enum(TransactionReason, native_enum=False)
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User")
