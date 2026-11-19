from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.filters import CommandObject
from aiogram.types import Message
from aiogram.types import User as TGUser
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from redis import ConnectionError
from src.attribution.schemas import Attribution
from src.attribution.service import (
    LOGIN_PREFIX,
    TOKEN_PREFIX,
    TOKEN_TTL_SECONDS,
    create_start_argument,
    resolve_start_argument,
)
from src.bot.menu.handlers import command_start
from src.config import settings
from src.models import User
from src.redis import Redis
from src.user import texts


def message_for(id: int) -> MagicMock:
    message = MagicMock(spec=Message)
    message.from_user = TGUser(id=id, is_bot=False, first_name="Alice")
    message.answer = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_landing_to_signup_notification(
    client: AsyncClient, session: AsyncSession, redis: Redis, mocker: MockerFixture
) -> None:
    enqueue = mocker.patch("src.user.service.enqueue_task")
    log = mocker.patch("src.user.service.log.info")
    response = await client.get(
        "/v1/attribution/start",
        params={"source": "telegram", "medium": "channel", "campaign": "launch <one>"},
    )
    assert response.status_code == 302
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    argument = response.headers["location"].split("?start=")[1]
    assert response.headers["location"].startswith(
        f"https://t.me/{settings.BOT_USERNAME}"
    )
    assert argument.startswith(LOGIN_PREFIX)
    assert len(argument) <= 64
    token = argument[len(LOGIN_PREFIX) :]
    assert 0 < await redis.ttl(TOKEN_PREFIX + token) <= TOKEN_TTL_SECONDS

    message = message_for(901001)
    await command_start(
        message, session, CommandObject(command="start", args=argument), redis
    )

    user = await session.get(User, 901001)
    assert user is not None
    assert user.signup_source == "telegram"
    assert user.signup_medium == "channel"
    assert user.signup_campaign == "launch <one>"
    log.assert_called_once_with(
        "New user",
        user_id=user.id,
        signup_source="telegram",
        signup_medium="channel",
        signup_campaign="launch <one>",
    )
    text = enqueue.call_args.kwargs["text"]
    assert "Source: telegram\nMedium: channel\nCampaign: launch &lt;one&gt;" in text
    # An attributed login must still issue the usual panel login link.
    assert (
        "bot-login?hash="
        in message.answer.call_args.kwargs["reply_markup"].inline_keyboard[0][0].url
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "argument", [None, "login", "login_a_bad", "login_a_" + "x" * 24]
)
async def test_missing_or_invalid_attribution_allows_signup(
    argument: str | None, session: AsyncSession, redis: Redis, mocker: MockerFixture
) -> None:
    enqueue = mocker.patch("src.user.service.enqueue_task")
    message = message_for(901002)
    await command_start(
        message, session, CommandObject(command="start", args=argument), redis
    )
    user = await session.get(User, 901002)
    assert user is not None
    assert user.signup_source is None
    assert enqueue.call_args.kwargs["text"] == texts.NEW_USER_LOG.format(
        id=user.id, full_name="Alice", username="--"
    )
    if argument:
        assert (
            "bot-login?hash="
            in message.answer.call_args.kwargs["reply_markup"].inline_keyboard[0][0].url
        )


@pytest.mark.asyncio
async def test_existing_user_keeps_signup_source(
    session: AsyncSession, user: User, redis: Redis, mocker: MockerFixture
) -> None:
    user.signup_source = "original"
    await session.flush()
    enqueue = mocker.patch("src.user.service.enqueue_task")
    argument = await create_start_argument(redis, Attribution(source="new"))
    await command_start(
        message_for(user.id),
        session,
        CommandObject(command="start", args=argument),
        redis,
    )
    assert user.signup_source == "original"
    enqueue.assert_not_called()


@pytest.mark.asyncio
async def test_existing_unattributed_user_is_not_backfilled(
    session: AsyncSession, user: User, redis: Redis
) -> None:
    argument = await create_start_argument(redis, Attribution(source="new"))
    await command_start(
        message_for(user.id),
        session,
        CommandObject(command="start", args=argument),
        redis,
    )
    assert user.signup_source is None


@pytest.mark.asyncio
async def test_direct_campaign_link(
    session: AsyncSession, mocker: MockerFixture
) -> None:
    mocker.patch.object(
        settings,
        "SIGNUP_CAMPAIGNS",
        {
            "channel_november": {
                "source": "telegram",
                "medium": "channel",
                "campaign": "november",
            }
        },
    )
    await command_start(
        message_for(901003),
        session,
        CommandObject(command="start", args="src_channel_november"),
    )
    user = await session.get(User, 901003)
    assert user is not None
    assert user.signup_source == "telegram"
    assert user.signup_campaign == "november"


@pytest.mark.asyncio
async def test_expired_and_corrupt_tokens(redis: Redis) -> None:
    argument = await create_start_argument(redis, Attribution(source="example.com"))
    token_key = TOKEN_PREFIX + argument[len(LOGIN_PREFIX) :]
    await redis.set(token_key, "not json")
    assert await resolve_start_argument(argument, redis) is None
    await redis.delete(token_key)
    assert await resolve_start_argument(argument, redis) is None


@pytest.mark.asyncio
async def test_redis_failure_does_not_break_login(
    client: AsyncClient, session: AsyncSession, redis: Redis, mocker: MockerFixture
) -> None:
    mocker.patch.object(redis, "set", side_effect=ConnectionError())
    mocker.patch.object(redis, "get", side_effect=ConnectionError())
    response = await client.get("/v1/attribution/start", params={"source": "telegram"})
    assert response.status_code == 302
    assert response.headers["location"].endswith("?start=login")
    await command_start(
        message_for(901004),
        session,
        CommandObject(command="start", args=LOGIN_PREFIX + "x" * 24),
        redis,
    )
    assert await session.get(User, 901004) is not None


@pytest.mark.asyncio
async def test_referrer_only_and_no_attribution(
    client: AsyncClient, redis: Redis
) -> None:
    response = await client.get("/v1/attribution/start")
    assert response.headers["location"].endswith("?start=login")
    response = await client.get(
        "/v1/attribution/start", params={"referrer": "example.com"}
    )
    argument = response.headers["location"].split("?start=")[1]
    attribution = await resolve_start_argument(argument, redis)
    assert attribution is not None
    assert attribution.referrer == "example.com"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    [
        {"source": "a" * 129},
        {"source": "bad\nvalue"},
        {"referrer": "https://example.com/private"},
    ],
)
async def test_invalid_query_values_are_rejected(
    client: AsyncClient, params: dict[str, str]
) -> None:
    response = await client.get("/v1/attribution/start", params=params)
    assert response.status_code == 422
