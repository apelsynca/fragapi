from uuid import UUID

from src.kit.repository import Options
from src.kit.repository.main import BaseRepository
from src.kit.repository.mixins import RepositoryIDMixin
from src.models import Payment


class PaymentRepository(RepositoryIDMixin[Payment, UUID], BaseRepository[Payment]):
    model = Payment

    async def get_by_hash(self, hash: str, *, options: Options = ()):
        stmt = self.get_base_stmt().where(self.model.hash == hash).options(*options)
        return await self.get_one_or_none(stmt=stmt)
