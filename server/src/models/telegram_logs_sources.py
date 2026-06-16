from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.kit.database.models import RecordModel

if TYPE_CHECKING:
    from .users import User


class TelegramLogsSource(RecordModel):
    __tablename__ = "telegram_logs_sources"

    chat_id: Mapped[str] = mapped_column(unique=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="telegram_logs_sources")

    __table_args__ = (UniqueConstraint("chat_id", "user_id"),)  # name default
