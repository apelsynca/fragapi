from .protocols import ModelIDProtocol, RepositoryProtocol


class IDRepositoryMixin[M: ModelIDProtocol, ID]:
    async def get_by_id(self: RepositoryProtocol[M], id: ID) -> M | None:
        stmt = self.get_base_stmt()
        stmt = stmt.where(self.model.id == id)

        return await self.get_one_or_none(stmt)
