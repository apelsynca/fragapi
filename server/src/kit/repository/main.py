from typing import Any

from sqlalchemy import Select, func, over, select
from sqlalchemy.ext.asyncio import AsyncSession


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

    async def update(self, obj: M, update_dict: dict[str, Any]) -> M:
        for attr, value in update_dict.items():
            setattr(obj, attr, value)

        self.session.add(obj)

        await self.session.commit()

        return obj

    async def create(self, obj: M) -> M:
        self.session.add(obj)

        await self.session.commit()
        await self.session.refresh(obj)

        return obj

    async def delete(self, obj: M) -> None:
        await self.session.delete(obj)
        await self.session.commit()

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
