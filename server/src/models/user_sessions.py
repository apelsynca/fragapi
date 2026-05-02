from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import settings
from src.kit.database.models import RecordModel
from src.kit.utils import utc_now

from .users import User

USER_SESSION_PREFIX = "pses"


def get_expires_at() -> datetime:
    return utc_now() + settings.user_session_ttl


class UserSession(RecordModel):
    token: Mapped[str] = mapped_column(unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True, default=get_expires_at
    )
    user_agent: Mapped[str | None] = mapped_column(Text)
    bot_hash: Mapped[str | None] = mapped_column(unique=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    user: Mapped[User] = relationship(User, lazy="joined")
