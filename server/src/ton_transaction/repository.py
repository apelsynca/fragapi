from uuid import UUID

from src.kit.repository import BaseRepository
from src.kit.repository.mixins import RepositoryIDMixin
from src.models import TonTransaction


class TonTransactionRepository(
    BaseRepository[TonTransaction], RepositoryIDMixin[TonTransaction, UUID]
):
    model = TonTransaction
