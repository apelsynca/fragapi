from src.kit.repository import BaseRepository
from src.models import TonTransaction


class TransactionRepository(BaseRepository[TonTransaction]):
    model = TonTransaction
