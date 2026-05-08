from src.kit.repository import Options

from .protocols import ModelIDProtocol, RepositoryProtocol


class IDRepositoryMixin[M: ModelIDProtocol, ID]:
    async def get_by_id(
        self: RepositoryProtocol[M], id: ID, *, options: Options = ()
    ) -> M | None:
        stmt = self.get_base_stmt().where(self.model.id == id).options(*options)
        return await self.get_one_or_none(stmt)
