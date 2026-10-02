import structlog
from aiogram.types import User as TGUser
from sqlalchemy.exc import IntegrityError

from src.exceptions import BadRequest, ResourceNotFound
from src.logging import Logger
from src.models import User
from src.postgres import AsyncSession
from src.telegram_log.tasks import admin_telegram_log_send
from src.user import texts
from src.user.repository import UserRepository
from src.worker import enqueue_task

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

        if tg_user.username:
            same_username_user = await repository.get_by_username(
                username=tg_user.username
            )
            if same_username_user is not None:
                log.warning(
                    "During creation from tg_user, user with the same username already existed",
                    username=tg_user.username,
                    existing_user_id=same_username_user.id,
                )
                same_username_user.username = None
                await session.flush()

        user = await repository.create(
            User(
                id=tg_user.id,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                username=tg_user.username,
                is_premium=tg_user.is_premium or False,
            ),
            flush=True,
        )

        enqueue_task(
            admin_telegram_log_send,
            text=texts.NEW_USER_LOG.format(
                id=user.id,
                full_name=user.full_name,
                username=f"@{user.username}" if user.username else "--",
            ),
            with_notification=False,
        )

        return user

    async def update_by_tg_user(
        self, session: AsyncSession, user: User, tg_user: TGUser
    ) -> User:
        if tg_user.is_bot:
            raise BadRequest("Telegram user is bot")

        if user.id != tg_user.id:
            raise BadRequest("User and telegram user have different id's")

        repository = UserRepository.from_session(session)

        update_dict = {
            "first_name": tg_user.first_name,
            "last_name": tg_user.last_name,
            "username": tg_user.username,
            "is_premium": tg_user.is_premium or False,
        }

        try:
            return await repository.update(user, update_dict=update_dict)
        except IntegrityError as error:
            constraint_name = getattr(error.orig, "constraint_name", None)

            if constraint_name == "users_username_key":
                # Someone else took this username, clear it and retry
                log.warning(
                    "Username conflict during update, clearing username",
                    user_id=user.id,
                    username=tg_user.username,
                )
                update_dict["username"] = None
                return await repository.update(user, update_dict=update_dict)
            else:
                raise


user = UserService()
