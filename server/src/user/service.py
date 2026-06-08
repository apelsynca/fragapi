import structlog
from aiogram.types import User as TGUser

from src.exceptions import BadRequest, ResourceNotFound
from src.logging import Logger
from src.models import User
from src.postgres import AsyncSession
from src.user.repository import UserRepository

log: Logger = structlog.get_logger()


class UserService:
    async def get_by_id(self, session: AsyncSession, id: int) -> User:
        repository = UserRepository.from_session(session)
        user = await repository.get_by_id(id=id)

        if user is None:
            raise ResourceNotFound("User not found")

        return user

    async def create_from_tg_user(
        self,
        session: AsyncSession,
        tg_user: TGUser,
    ) -> User:
        if tg_user.is_bot:
            raise BadRequest("Cannot create from tg_user which is bot")

        repository = UserRepository.from_session(session)

        return await repository.create(
            User(
                id=tg_user.id,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                username=tg_user.username,
                is_premium=tg_user.is_premium or False,
            ),
            flush=True,
        )


user = UserService()
