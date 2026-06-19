from src.kit.repository import BaseRepository
from src.models import TonTransaction


class TonTransactionRepository(BaseRepository[TonTransaction]):
    model = TonTransaction
