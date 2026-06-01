from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from src.kit.database.models import RecordModel
from src.kit.utils import generate_api_token

if TYPE_CHECKING:
    from .users import User


class ApiToken(RecordModel):
    __tablename__ = "api_tokens"

    name: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(unique=True, default=generate_api_token)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship("User", lazy="raise")

    expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, index=True
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )
