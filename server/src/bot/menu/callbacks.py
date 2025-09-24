from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram import User as TGUser
from telegram.ext import Application, CommandHandler, ContextTypes

from src.auth.repository import UserSessionRepository
from src.auth.service import AuthService
from src.bot.utils import with_session
from src.config import settings
from src.exceptions import ResourceNotFound
from src.models.users import User
from src.users.repository import UserRepository
from src.users.schemas import UserCreate
from src.users.service import UserService

LOGIN_ARG = "login"


@with_session
async def menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE, session: AsyncSession
) -> None:
    message = cast(Message, update.message)
    e_user = cast(TGUser, update.effective_user)

    user_service = UserService(repository=UserRepository(session=session))

    try:
        user = await user_service.get(id=e_user.id)
    except ResourceNotFound:
        user = await user_service.create(
            user=UserCreate(
                id=e_user.id,
                first_name=e_user.first_name,
                last_name=e_user.last_name,
                username=e_user.username,
                is_premium=e_user.is_premium or False,
            )
        )

    if context.args and context.args[0] == LOGIN_ARG:
        return await login(update, user, session)

    await message.reply_text(
        text=f"Привет, {e_user.mention_html()}",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Доки", url=settings.docs_url),
                    InlineKeyboardButton(text="Панель", url=settings.panel_url),
                ]
            ]
        ),
    )


async def login(update: Update, user: User, session: AsyncSession) -> None:
    message = cast(Message, update.message)

    auth_service = AuthService(
        session_repository=UserSessionRepository(session=session)
    )
    login_data = await auth_service.login(user=user, with_bot_hash=True)

    await message.reply_text(
        text="Авторизация прошла успешно!\n\nНажмите войти 👇",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Войти",
                        url=f"{settings.panel_url}/login?hash={login_data.bot_hash}",
                    )
                ]
            ]
        ),
    )


def setup_callbacks(application: Application):
    application.add_handler(CommandHandler({"start", "menu"}, menu))
