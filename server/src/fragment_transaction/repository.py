from uuid import UUID

from src.kit.repository.main import BaseRepository
from src.kit.repository.mixins import IDRepositoryMixin
from src.models.fragment_transactions import FragmentTransaction


class FragmentTransactionRepository(
    BaseRepository[FragmentTransaction], IDRepositoryMixin[FragmentTransaction, UUID]
):
    model = FragmentTransaction
