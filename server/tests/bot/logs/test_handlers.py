import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.logs import texts
from src.bot.logs.handlers import get_menu_info
from src.bot.logs.keyboards import get_menu_keyboard
from src.models import User


@pytest.mark.asyncio
async def test_get_logs_info_text_and_keyboard_empty(
    session: AsyncSession, user: User
) -> None:
    text, reply_markup = await get_menu_info(session=session, user=user)

    assert text == texts.INFO_ABOUT_LOGS.format(status=texts.STATUS_UNSET)
    assert reply_markup == get_menu_keyboard()
