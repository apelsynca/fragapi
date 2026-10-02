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

        try:
            async with session.begin_nested():
                user = await repository.create(User(**user_data), flush=True)
        except IntegrityError as error:
            constraint_name = getattr(error.orig, "constraint_name", None)

            # Two updates can both observe a missing Telegram user before either
            # transaction commits. Reuse the row created by the other update.
            if constraint_name == "users_pkey":
                user = await repository.get_by_id(id=tg_user.id)
                if user is None:
                    raise
                log.warning(
                    "User already exists while creating from Telegram user",
                    user_id=tg_user.id,
                )
            elif constraint_name == "users_username_key":
                # Telegram can recycle usernames while an old row still has the
                # value. Release it from the old row before creating the new one.
                try:
                    async with session.begin_nested():
                        previous_user = await session.scalar(
                            select(User).where(User.username == tg_user.username)
                        )
                        if previous_user is None:
                            raise

                        previous_user.username = None
                        await session.flush()
                        user = await repository.create(User(**user_data), flush=True)
                except IntegrityError:
                    # Another concurrent request already handled the username conflict
                    # or created this user. Fetch the existing user.
                    user = await repository.get_by_id(id=tg_user.id)
                    if user is None:
                        raise
                    log.warning(
                        "User created by concurrent request during username conflict resolution",
                        user_id=tg_user.id,
                        username=tg_user.username,
                    )
            else:
                raise

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
        return await repository.update(
            user,
            update_dict={
                "first_name": tg_user.first_name,
                "last_name": tg_user.last_name,
                "username": tg_user.username,
                "is_premium": tg_user.is_premium or False,
            },
        )


user = UserService()
