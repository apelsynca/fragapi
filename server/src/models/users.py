from typing import TYPE_CHECKING

from aiogram import html
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import UserRole
from src.kit.database.models import TimestampedModel

if TYPE_CHECKING:
    from .telegram_logs_sources import TelegramLogsSource
    from .transactions import Transaction


class User(TimestampedModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None] = mapped_column(unique=True)
    is_premium: Mapped[bool] = mapped_column(default=False)

    balance: Mapped[float] = mapped_column(default=0)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")

    telegram_logs_sources: Mapped[list["TelegramLogsSource"]] = relationship(
        back_populates="user"
    )

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def html_telegram_link(self) -> str:
        return (
            f"<a href='tg://resolve?domain={self.username}'>{html.quote(self.first_name)}</a>"
            if self.username
            else f"<a href='tg://user?id={self.id}'>{html.quote(self.first_name)}</a>"
        )
