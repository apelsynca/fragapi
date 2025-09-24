from src.kit.repository import BaseRepository
from src.models import UserSession


class UserSessionRepository(BaseRepository[UserSession]):
    model = UserSession
