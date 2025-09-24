from src.kit.repository import BaseRepository, IDRepositoryMixin
from src.models import User


class UserRepository(BaseRepository[User], IDRepositoryMixin[User, int]):
    model = User
