from typing import Any, Protocol

from sqlalchemy import Select
from sqlalchemy.orm import Mapped


class RepositoryProtocol[M](Protocol):
    model: type[M]

    def get_base_stmt(self) -> Select[tuple[M]]: ...

    async def get_one_or_none(self, stmt: Select[tuple[M]]) -> M | None: ...

    async def get_all(self, stmt: Select[tuple[M]]) -> list[M]: ...

    async def update(
        self, obj: M, *, update_dict: dict[str, Any], flush: bool = False
    ) -> M: ...

    async def create(self, obj: M, *, flush: bool = False) -> M: ...

    async def delete(self, obj: M) -> None: ...

    async def paginate(
        self, stmt: Select[tuple[M]], limit: int, page: int
    ) -> tuple[list[M], int]: ...

    async def count(self, stmt: Select[tuple[M]]) -> int: ...


class ModelIDProtocol[ID_TYPE](Protocol):
    id: Mapped[ID_TYPE]
