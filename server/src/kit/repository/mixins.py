from enum import StrEnum
from typing import Any

from sqlalchemy import ColumnExpressionArgument, Select, UnaryExpression, asc, desc

from src.kit.repository import Options
from src.kit.sorting import Sorting

from .protocols import ModelIDProtocol, RepositoryProtocol


class RepositoryIDMixin[M: ModelIDProtocol, ID]:
    async def get_by_id(
        self: RepositoryProtocol[M], id: ID, *, options: Options = ()
    ) -> M | None:
        stmt = self.get_base_stmt().where(self.model.id == id).options(*options)
        return await self.get_one_or_none(stmt)


type SortingClause = ColumnExpressionArgument[Any] | UnaryExpression[Any]


class RepositorySortingMixin[M, PE: StrEnum]:
    sorting_enum: type[PE]

    def apply_sorting(
        self,
        stmt: Select[tuple[M]],
        sorting: list[Sorting[PE]],
    ) -> Select[tuple[M]]:
        order_by_clauses: list[UnaryExpression[Any]] = []
        for criterion, is_desc in sorting:
            clause_function = desc if is_desc else asc
            order_by_clauses.append(clause_function(self.get_sorting_clause(criterion)))
        return stmt.order_by(*order_by_clauses)

    def get_sorting_clause(self, property: PE) -> SortingClause:
        raise NotImplementedError()
