import pytest
from aiogram.types import User as TGUser
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BadRequest
from src.user.service import user as user_service


@pytest.mark.asyncio
async def test_creates_from_tg_user(session: AsyncSession) -> None:
    tg_user = TGUser(
        id=99299, is_bot=False, first_name="Homo Citrus", username="homocitrus"
    )

    user = await user_service.create_from_tg_user(session=session, tg_user=tg_user)

    assert user.id == 99299
    assert user.first_name == "Homo Citrus"
    assert user.username == "homocitrus"
    assert user.balance == 0


@pytest.mark.asyncio
async def test_create_from_tg_user_raises_if_is_bot(session: AsyncSession) -> None:
    tg_user = TGUser(
        id=99299, is_bot=True, first_name="Sanek", username="sanechka_snimayesh"
    )

    with pytest.raises(BadRequest):
        await user_service.create_from_tg_user(session=session, tg_user=tg_user)
