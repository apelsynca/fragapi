from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.filters import CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types import User as TGUser
from freezegun import freeze_time
from pytest_mock import MockerFixture
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.menu.handlers import (
    AUTHORIZATION_SUCCESS_TEXT,
    command_start,
    login,
    user_service,
)
from src.config import settings
from src.kit.utils import utc_now
from src.models import User, UserSession


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
