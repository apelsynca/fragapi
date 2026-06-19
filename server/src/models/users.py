from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import UserRole
from src.kit.database.models import TimestampedModel

if TYPE_CHECKING:
    from .telegram_logs_sources import TelegramLogsSource
    from .transactions import FragmentTransaction


class User(TimestampedModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None] = mapped_column(unique=True)
    is_premium: Mapped[bool] = mapped_column(default=False)

    balance: Mapped[float] = mapped_column(default=0)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    fragment_transactions: Mapped[list["FragmentTransaction"]] = relationship(
        "FragmentTransaction", back_populates="user"
    )

    telegram_logs_sources: Mapped[list["TelegramLogsSource"]] = relationship(
        "TelegramLogsSource", back_populates="user"
    )
