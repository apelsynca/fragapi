import secrets
from typing import cast

import structlog
from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.types import User as TGUser
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.exceptions import ResourceNotFound
from src.kit.crypto import generate_token
from src.logging import Logger
from src.models import User, UserSession
from src.models.user_sessions import USER_SESSION_PREFIX
from src.user.service import user as user_service

router = Router(name="menu")

log: Logger = structlog.get_logger()

LOGIN_ARG = "login"
AUTHORIZATION_SUCCESS_TEXT = "🚪 Авторизовал.\n\nЧтобы войти кнопка снизу 👇"


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
        text=f"Привет, <b>{tg_user.full_name}</b>\n\nБаланс: <b>{user.balance:.2f} TON</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🌐 Панель", url=settings.PANEL_URL)],
                [InlineKeyboardButton(text="📃 Документация", url=settings.DOCS_URL)],
                [
                    InlineKeyboardButton(
                        text="🔔 Уведомления", callback_data="notifications"
                    )
                ],
            ]
        ),
    )


async def login(message: Message, session: AsyncSession, user: User) -> None:
    user_session = UserSession(
        user=user,
        user_agent=None,
        token=generate_token(prefix=USER_SESSION_PREFIX),
        bot_hash=secrets.token_urlsafe(24),
    )
    session.add(user_session)
    await session.flush()

    await message.answer(
        text=AUTHORIZATION_SUCCESS_TEXT,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Войти",
                        url=f"{settings.PANEL_URL}/bot-login?hash={user_session.bot_hash}",
                    )
                ]
            ]
        ),
    )


@router.callback_query()
async def notifications_empty(callback_query: CallbackQuery) -> None:
    await callback_query.answer(text="Coming soon...", show_alert=True)
