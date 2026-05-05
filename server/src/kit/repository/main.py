from collections.abc import Sequence
from typing import Any, Self

from sqlalchemy import Select, func, over, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

type Options = Sequence[ExecutableOption]


class BaseRepository[M]:
    model: type[M]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_base_stmt(self) -> Select[tuple[M]]:
        return select(self.model)

    async def get_one_or_none(self, stmt: Select[tuple[M]]) -> M | None:
        return await self.session.scalar(stmt)

    async def get_all(self, stmt: Select[tuple[M]]) -> list[M]:
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

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
        pagination_stmt: Select[tuple[M, int]] = (
            stmt.add_columns(over(func.count())).limit(limit).offset(offset)
        )
        results = await self.session.stream(pagination_stmt)

        items: list[M] = []
        count = 0

        async for result in results.unique():
            item, count = result._tuple()
            items.append(item)

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
