import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import ResourceNotFound
from src.kit.utils import generate_api_key
from src.logging import Logger
from src.models import User
from src.user.repository import UserRepository
from src.user.schemas import UserCreate

log: Logger = structlog.get_logger()


class UserService:
    async def get_by_id(self, session: AsyncSession, id: int) -> User:
        repository = UserRepository.from_session(session)
        user = await repository.get_by_id(id=id)

        if user is None:
            raise ResourceNotFound("User not found")

        return user

    async def create(self, session: AsyncSession, user: UserCreate) -> User:
        repository = UserRepository.from_session(session)
        log.info(
            "Creating user",
            user_id=user.id,
            first_name=user.first_name,
            username=user.username,
        )

        return await repository.create(
            User(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                is_premium=user.is_premium,
                api_key=generate_api_key(),
            )
        )


user = UserService()
