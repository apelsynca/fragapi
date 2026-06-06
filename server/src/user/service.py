import structlog

from src.exceptions import ResourceNotFound
from src.logging import Logger
from src.models import User
from src.postgres import AsyncSession
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

    async def create(self, session: AsyncSession, data: UserCreate) -> User:
        repository = UserRepository.from_session(session)
        log.info(
            "Creating user",
            user_id=data.id,
            first_name=data.first_name,
            username=data.username,
        )

        return await repository.create(
            User(
                id=data.id,
                first_name=data.first_name,
                last_name=data.last_name,
                username=data.username,
                is_premium=data.is_premium,
            )
        )


user = UserService()
