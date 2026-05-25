from collections.abc import Sequence
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_token.schemas import ApiTokenCreate
from src.api_token.service import api_token as api_token_service
from src.exceptions import BadRequest, ResourceNotFound
from src.kit.utils import utc_now
from src.models import ApiToken, User
from tests.fixtures.database import SaveFixture


@pytest.mark.asyncio
async def test_get_by_user(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    api_token = ApiToken(
        name="Development",
        user=user,
        token="SomeTokenValue",
        last_used_at=datetime(year=2026, month=5, day=20),
    )
    await save_fixture(api_token)

    api_tokens = await api_token_service.get_by_user(session=session, user=user)

    assert isinstance(api_tokens, Sequence)
    assert len(api_tokens) == 1


@pytest.mark.asyncio
async def test_get_by_user_right_user(
    save_fixture: SaveFixture, session: AsyncSession, user: User, user_second: User
) -> None:
    wrong_api_token = ApiToken(
        name="Development",
        user=user_second,
        token="SomeTokenValue",
    )
    await save_fixture(wrong_api_token)
    api_token = ApiToken(
        name="Development",
        user=user,
        token="SomeTokenValue",
    )
    await save_fixture(api_token)

    api_tokens = await api_token_service.get_by_user(session=session, user=user)

    assert isinstance(api_tokens, Sequence)
    assert len(api_tokens) == 1


@pytest.mark.asyncio
async def test_create_for_user(session: AsyncSession, user: User) -> None:
    exp_at = utc_now() + timedelta(days=10)

    api_token = await api_token_service.create(
        session=session,
        user=user,
        data=ApiTokenCreate(name="Development", expires_at=exp_at),
    )

    assert api_token.name == "Development"
    assert api_token.expires_at == exp_at


@pytest.mark.asyncio
async def test_cannot_create_already_expired(session: AsyncSession, user: User) -> None:
    exp_at = utc_now() - timedelta(minutes=1)

    with pytest.raises(BadRequest):
        await api_token_service.create(
            session=session,
            user=user,
            data=ApiTokenCreate(name="Development", expires_at=exp_at),
        )


@pytest.mark.asyncio
async def test_delete_api_key(
    save_fixture: SaveFixture, session: AsyncSession, user: User
) -> None:
    api_token = ApiToken(
        name="Development",
        user=user,
        token="SomeTokenValue",
    )
    await save_fixture(api_token)

    await api_token_service.delete(session=session, user=user, id=api_token.id)

    found_api_token = await session.scalar(
        select(ApiToken).where(ApiToken.id == api_token.id)
    )

    assert found_api_token is None


@pytest.mark.asyncio
async def test_raises_not_found_if_tries_to_delete_wrong_api_key(
    save_fixture, session, user, user_second
) -> None:
    api_token = ApiToken(
        name="Development",
        user=user,
        token="SomeTokenValue",
    )
    await save_fixture(api_token)

    with pytest.raises(ResourceNotFound):
        await api_token_service.delete(
            session=session, user=user_second, id=api_token.id
        )
