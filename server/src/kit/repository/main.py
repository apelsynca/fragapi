from collections.abc import Sequence
from typing import Any, Self

from sqlalchemy import Select, func, select
from sqlalchemy.sql.base import ExecutableOption

from src.kit.pagination import count_subquery
from src.postgres import AsyncSession

type Options = Sequence[ExecutableOption]


class BaseRepository[M]:
    model: type[M]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_base_stmt(self) -> Select[tuple[M]]:
        return select(self.model)

    async def get_one_or_none(self, stmt: Select[tuple[M]]) -> M | None:
        return await self.session.scalar(stmt)

    async def get_all(self, stmt: Select[tuple[M]]) -> Sequence[M]:
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def update(
        self, obj: M, *, update_dict: dict[str, Any], flush: bool = False
    ) -> M:
        for attr, value in update_dict.items():
            setattr(obj, attr, value)

        self.session.add(obj)

        if flush:
            await self.session.flush()

        return obj

    async def create(self, obj: M, *, flush: bool = False) -> M:
        self.session.add(obj)

        if flush:
            await self.session.flush()

        return obj

    async def delete(self, obj: M) -> None:
        await self.session.delete(obj)

    async def paginate(
        self, stmt: Select[tuple[M]], limit: int, page: int
    ) -> tuple[list[M], int]:
        offset = (page - 1) * limit

        count_statement = select(func.count()).select_from(count_subquery(stmt))
        count_result = await self.session.execute(count_statement)
        count = count_result.scalar_one()

        paginated_statement = stmt.limit(limit).offset(offset)
        # Streaming can't be applied here, since we need to call ORM's unique()
        results = await self.session.execute(paginated_statement)
        items = list(results.unique().scalars().all())
        return items, count

    async def count(self, stmt: Select[tuple[M]]) -> int:
        count_statement = stmt.with_only_columns(
            func.count(), maintain_column_froms=True
        )
        result = await self.session.execute(count_statement)
        return result.scalar_one()

    @classmethod
    def from_session(cls, session: AsyncSession) -> Self:
        return cls(session)
