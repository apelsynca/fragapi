from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import UserRole
from src.kit.database.models import RecordModel
from src.kit.utils import generate_api_key

if TYPE_CHECKING:
    from .transactions import Transaction


class User(RecordModel):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None] = mapped_column(unique=True)
    is_premium: Mapped[bool] = mapped_column(default=False)

    balance: Mapped[float] = mapped_column(default=0)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    api_key: Mapped[str] = mapped_column(unique=True, default=generate_api_key)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user"
    )
