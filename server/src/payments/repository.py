from src.kit.repository.main import BaseRepository
from src.models import Payment


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    async def get_by_hash(self, hash: str) -> Payment | None:
        stmt = self.get_base_stmt().where(Payment.hash == hash)

        return await self.get_one_or_none(stmt)
