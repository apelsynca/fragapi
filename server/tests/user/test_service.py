import pytest
from aiogram.types import User as TGUser
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BadRequest
from src.models import User
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


@pytest.mark.asyncio
async def test_update_by_tg_user_changes_fields(
    session: AsyncSession, user: User
) -> None:
    tg_user = TGUser(
        id=user.id, is_bot=False, first_name="MyNewName", username="homocitrus"
    )

    user = await user_service.update_by_tg_user(
        session=session, user=user, tg_user=tg_user
    )

    assert user.first_name == "MyNewName"
    assert user.username == "homocitrus"
    assert user.last_name == user.last_name
    assert user.is_premium == user.is_premium

    found_user = await session.get_one(User, user.id)
    assert found_user.first_name == "MyNewName"
    assert found_user.username == "homocitrus"


@pytest.mark.asyncio
async def test_update_by_tg_user_raises_if_different_id(
    session: AsyncSession, user: User
) -> None:
    tg_user = TGUser(
        id=99599,
        is_bot=False,
        first_name="SomeName",
        username="homocitrus",
        last_name="MyLastName",
    )

    with pytest.raises(BadRequest, match="different id"):
        await user_service.update_by_tg_user(
            session=session, user=user, tg_user=tg_user
        )

    found_user = await session.get_one(User, user.id)
    assert found_user.first_name != "SomeName"
    assert found_user.last_name != "MyLastName"
    assert found_user.username != "homocitrus"


@pytest.mark.asyncio
async def test_update_by_tg_user_raises_if_bot(
    session: AsyncSession, user: User
) -> None:
    tg_user = TGUser(
        id=44144, is_bot=True, first_name="MyNewName", username="homocitrus"
    )

    with pytest.raises(BadRequest, match="is bot"):
        await user_service.update_by_tg_user(
            session=session, user=user, tg_user=tg_user
        )

    found_user = await session.get_one(User, user.id)
    assert found_user.first_name == user.first_name
    assert found_user.last_name == user.last_name
    assert found_user.username == user.username
