from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.filters import CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types import User as TGUser
from freezegun import freeze_time
from pytest_mock import MockerFixture
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot import custom_emoji
from src.bot.menu import texts
from src.bot.menu.handlers import command_start, login, user_service
from src.config import settings
from src.kit.utils import utc_now
from src.models import User, UserSession
from src.user.service import UserService


@pytest.mark.asyncio
async def test_command_start_updates_user(
    session: AsyncSession, user: User, mocker: MockerFixture
) -> None:
    update_by_tg_user_spy = mocker.spy(user_service, "update_by_tg_user")

    message = MagicMock(spec=Message)
    message.from_user = TGUser(
        id=user.id, is_bot=False, first_name="Apple Synca", username="diffiesynca"
    )
    message.answer = AsyncMock()

    command = MagicMock(spec=CommandObject)

    await command_start(message=message, session=session, command=command)

    update_by_tg_user_spy.assert_called_once_with(
        session=session, user=user, tg_user=message.from_user
    )

    assert user.first_name == "Apple Synca"
    assert user.username == "diffiesynca"


@pytest.mark.asyncio
async def test_login_creates_user_session(session: AsyncSession, user: User) -> None:
    message = MagicMock(spec=Message)
    message.answer = AsyncMock()

    # when
    await login(message=message, session=session, user=user)

    user_session = await session.scalar(
        select(UserSession).where(UserSession.user == user)
    )
    assert user_session is not None
    assert user_session.bot_hash is not None

    message.answer.assert_called_once_with(
        text=texts.AUTHORIZATION_SUCCESS,
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


@freeze_time("2025-01-14")
@pytest.mark.asyncio
async def test_expires(session: AsyncSession, user: User) -> None:
    message = MagicMock(spec=Message)
    message.answer = AsyncMock()

    # when
    await login(message=message, session=session, user=user)

    user_session = await session.scalar(
        select(UserSession).where(UserSession.user == user)
    )

    assert user_session is not None
    assert user_session.expires_at == utc_now() + settings.BOT_LOGIN_SESSION_TTL


@pytest.mark.asyncio
async def test_menu_authorized_answers_right_text_and_keyboard(
    session: AsyncSession, mocker: MockerFixture, user: User
) -> None:
    message = MagicMock(spec=Message)
    message.answer = AsyncMock()
    message.from_user = TGUser(is_bot=False, id=-1, first_name="Firstiie")

    user_service_mock = mocker.patch(
        "src.bot.menu.handlers.user_service", spec=UserService
    )
    # NOTE: this is anti pattern i guess
    user_service_mock.get_by_id.return_value = user
    user_service_mock.update_by_tg_user.return_value = user

    await command_start(message, session, CommandObject(command="start"))

    message.answer.assert_called_once_with(
        text=texts.MENU.format(
            emoji=custom_emoji.FRAGMENT_ANIMATED.html,
            full_name="Firstiie",
            balance=user.balance,
            channel_url=settings.TELEGRAM_CHANNEL_URL,
            chat_url=settings.TELEGRAM_CHAT_URL,
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🌐 Панель",
                        url=settings.generate_panel_url("/"),
                        style="primary",
                    )
                ],
                [InlineKeyboardButton(text="📃 Документация", url=settings.DOCS_URL)],
                [
                    InlineKeyboardButton(
                        text="📄 Логи о транзакциях", callback_data="logs"
                    )
                ],
            ]
        ),
    )
