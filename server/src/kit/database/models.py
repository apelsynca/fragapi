import re
from datetime import datetime

from sqlalchemy import DateTime, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.kit.utils import utc_now


class Model(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class IDModel(Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    def __hash__(self) -> int:
        return self.id

    def __repr__(self) -> str:
        insp = inspect(self)
        if insp.identity is not None:
            id_value = insp.identity[0]
            return f"{self.__class__.__name__}(id={id_value!r})"
        return f"{self.__class__.__name__}(id=None)"


class TimestampedModel(Model):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=utc_now, nullable=True, default=None
    )


class RecordModel(IDModel, TimestampedModel):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically resolves `__tablename__`
        (camelCase -> snake_case) + optional 's'
        """
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        if not name.endswith("s"):
            return name + "s"
        return name
