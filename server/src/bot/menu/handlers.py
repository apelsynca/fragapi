import secrets
from typing import cast

import structlog
from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import (
    Message,
)
from aiogram.types import User as TGUser
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.menu import keyboards, texts
from src.config import settings
from src.exceptions import ResourceNotFound
from src.kit.crypto import generate_token
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import User, UserSession
from src.models.user_sessions import USER_SESSION_PREFIX
from src.user.service import user as user_service

router = Router(name="menu")

log: Logger = structlog.get_logger()

LOGIN_ARG = "login"


@router.message(CommandStart())
async def command_start(
    message: Message, session: AsyncSession, command: CommandObject
) -> None:
    tg_user = cast(TGUser, message.from_user)

    try:
        user = await user_service.get_by_id(session=session, id=tg_user.id)
        user = await user_service.update_by_tg_user(
            session=session, user=user, tg_user=tg_user
        )
    except ResourceNotFound:
        user = await user_service.create_from_tg_user(session=session, tg_user=tg_user)

    if command.args is not None and command.args == LOGIN_ARG:
        return await login(message=message, session=session, user=user)

    await message.answer(
        text=texts.MENU.format(full_name=tg_user.full_name, balance=user.balance),
        reply_markup=keyboards.panel(),
    )


async def login(message: Message, session: AsyncSession, user: User) -> None:
    user_session = UserSession(
        user=user,
        user_agent=None,
        token=generate_token(prefix=USER_SESSION_PREFIX),
        bot_hash=secrets.token_urlsafe(24),
        expires_at=utc_now() + settings.BOT_LOGIN_SESSION_TTL,
    )
    session.add(user_session)
    await session.flush()

    assert user_session.bot_hash is not None

    await message.answer(
        text=texts.AUTHORIZATION_SUCCESS,
        reply_markup=keyboards.login(bot_hash=user_session.bot_hash),
    )
