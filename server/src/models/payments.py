from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .users import User


# i know here ID could be changed and used as hash
class Payment(RecordModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", lazy="joined")

    amount: Mapped[float]
    hash: Mapped[str] = mapped_column(unique=True)
