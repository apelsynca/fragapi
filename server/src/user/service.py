import structlog
from aiogram.types import User as TGUser
from sqlalchemy import select
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

        user_data = {
            "id": tg_user.id,
            "first_name": tg_user.first_name,
            "last_name": tg_user.last_name,
            "username": tg_user.username,
            "is_premium": tg_user.is_premium or False,
        }

        is_new_user = False
        try:
            async with session.begin_nested():
                user = await repository.create(User(**user_data), flush=True)
                is_new_user = True
        except IntegrityError as error:
            constraint_name = getattr(error.orig, "constraint_name", None)

            if constraint_name == "users_pkey":
                # Concurrent request already created this user
                log.warning(
                    "User already exists while creating from Telegram user",
                    user_id=tg_user.id,
                )
                user = await self.get_by_id(session=session, id=tg_user.id)
            elif constraint_name == "users_username_key":
                user = await self._handle_username_conflict(
                    session, repository, tg_user, user_data
                )
            else:
                raise

        # Only notify on actual new user creation
        if is_new_user:
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

    async def _handle_username_conflict(
        self,
        session: AsyncSession,
        repository: UserRepository,
        tg_user: TGUser,
        user_data: dict,
    ) -> User:
        """Handle username constraint conflict - either concurrent creation or username recycling."""
        existing_user = await session.scalar(
            select(User).where(User.username == tg_user.username)
        )
        if existing_user is None:
            raise ResourceNotFound(
                f"Username conflict detected but user with username '{tg_user.username}' not found"
            )

        if existing_user.id == tg_user.id:
            # Concurrent request already created this exact user
            log.warning(
                "User already created by concurrent request",
                user_id=tg_user.id,
                username=tg_user.username,
            )
            return existing_user

        # Telegram recycled the username to a different user
        # Release it from the old row and create the new user
        try:
            async with session.begin_nested():
                existing_user.username = None
                await session.flush()
                return await repository.create(User(**user_data), flush=True)
        except IntegrityError:
            # Another concurrent request handled this - fetch the result
            log.warning(
                "User created by concurrent request during username recycling",
                user_id=tg_user.id,
                username=tg_user.username,
            )
            return await self._fetch_existing_user(repository, tg_user.id)

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
