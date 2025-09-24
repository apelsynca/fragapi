from src.kit.repository.id_mixin import IDRepositoryMixin
from src.kit.repository.main import BaseRepository
from src.models import Transaction


class TransactionRepository(
    BaseRepository[Transaction], IDRepositoryMixin[Transaction, int]
):
    model = Transaction
