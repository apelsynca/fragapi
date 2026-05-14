import secrets
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram import User as TGUser
from telegram.ext import Application, CommandHandler, ContextTypes

from src.bot.utils.decorators import with_session
from src.config import settings
from src.exceptions import ResourceNotFound
from src.kit.crypto import generate_token
from src.models.user_sessions import USER_SESSION_PREFIX, UserSession
from src.models.users import User
from src.users.schemas import UserCreate
from src.users.service import user as user_service

LOGIN_ARG = "login"


@with_session
async def menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: AsyncSession
) -> None:
    message = cast(Message, update.message)
    e_user = cast(TGUser, update.effective_user)

    try:
        user = await user_service.get_by_id(session=session, id=e_user.id)
    except ResourceNotFound:
        user = await user_service.create(
            session=session,
            user=UserCreate(
                id=e_user.id,
                first_name=e_user.first_name,
                last_name=e_user.last_name,
                username=e_user.username,
                is_premium=e_user.is_premium or False,
            ),
        )

    if context.args and context.args[0] == LOGIN_ARG:
        return await login(update, user, session)

    await message.reply_text(
        text=f"Привет, {e_user.mention_html()}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Доки", url=settings.DOCS_URL),
                    InlineKeyboardButton(text="Панель", url=settings.PANEL_URL),
                ]
            ]
        ),
    )


async def login(update: Update, user: User, session: AsyncSession) -> None:
    message = cast(Message, update.message)

    user_session = UserSession(
        user=user,
        user_agent=None,
        token=generate_token(prefix=USER_SESSION_PREFIX),
        bot_hash=secrets.token_urlsafe(24),
    )

    session.add(user_session)
    await session.commit()
    await session.refresh(user_session)

    await message.reply_text(
        text="Авторизация прошла успешно!\n\nНажмите войти 👇",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Войти",
                        url=f"{settings.PANEL_URL}/bot-login?hash={user_session.bot_hash}",
                    )
                ]
            ]
        ),
    )


def setup_callbacks(application: Application):
    application.add_handler(CommandHandler({"start", "menu"}, menu))
