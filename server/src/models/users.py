from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.enums import UserRole
from src.kit.models import RecordModel


class User(RecordModel):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    first_name: Mapped[str]
    last_name: Mapped[str | None]
    username: Mapped[str | None] = mapped_column(unique=True)
    is_premium: Mapped[bool] = mapped_column(default=False)

    balance: Mapped[float] = mapped_column(default=0)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    api_key: Mapped[str] = mapped_column(unique=True)
