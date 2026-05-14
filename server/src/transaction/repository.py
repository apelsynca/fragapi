from src.kit.repository import BaseRepository
from src.models import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    model = Transaction
