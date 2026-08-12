from datetime import datetime
from uuid import UUID

from sqlalchemy import TIMESTAMP, Uuid, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.kit.utils import generate_uuid, utc_now


class Model(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class IDModel(Model):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=generate_uuid)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __hash__(self) -> int:
        return self.id.int

    def __repr__(self) -> str:
        # We do this complex thing because we might be outside a session with
        # an expired object;
        # But basically, we want to show the ID if we have it.
        insp = inspect(self)
        if insp.identity is not None:
            id_value = insp.identity[0]
            return f"{self.__class__.__name__}(id={id_value!r})"
        return f"{self.__class__.__name__}(id=None)"

    @classmethod
    def generate_id(cls) -> UUID:
        return generate_uuid()


class TimestampedModel(Model):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=utc_now, index=True
    )
    modified_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), onupdate=utc_now, nullable=True, default=None
    )

    def set_modified_at(self) -> None:
        self.modified_at = utc_now()

    def set_deleted_at(self) -> None:
        self.deleted_at = utc_now()


class RecordModel(IDModel, TimestampedModel):
    __abstract__ = True
