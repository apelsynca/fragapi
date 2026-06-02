import pytest
from sqlalchemy import select

from src.auth.service import auth as auth_service
from src.exceptions import Forbidden
from src.models import User
from src.models.user_sessions import UserSession
from src.postgres import AsyncSession
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_api_token, rstr


@pytest.mark.asyncio
async def test_login_by_bot_hash_random_raises(session: AsyncSession) -> None:
    with pytest.raises(Forbidden):
        await auth_service.login_by_bot_hash(
            session=session, bot_hash=rstr("someWrong")
        )


@pytest.mark.asyncio
async def test_login_by_bot_hash_deletes_old_and_creates_new_us(
    session: AsyncSession, user: User, save_fixture: SaveFixture
) -> None:
    user_session = UserSession(token=rstr("anytoken"), bot_hash="mybothash", user=user)
    await save_fixture(user_session)
    assert user_session.bot_hash is not None

    login_response = await auth_service.login_by_bot_hash(
        session=session, bot_hash=user_session.bot_hash
    )

    assert login_response.token != user_session.token

    stmt = select(UserSession).where(UserSession.bot_hash == "mybothash")
    orig_user_session = await session.scalar(stmt)

    assert orig_user_session is None

    stmt = select(UserSession).where(UserSession.token == login_response.token)
    new_user_session = await session.scalar(stmt)

    assert new_user_session is not None
    assert new_user_session.token == login_response.token


@pytest.mark.asyncio
async def test_authenticate_by_api_token_gets_user(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    api_token = await create_api_token(save_fixture, user=user)
    returned_user = await auth_service.authenticate_by_api_token(
        session=session, token=api_token.token
    )

    assert returned_user == user
