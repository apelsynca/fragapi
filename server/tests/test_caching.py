from unittest.mock import AsyncMock, MagicMock

import pytest

from src.caching import premium_recipient_cache, stars_recipient_cache
from src.config import settings
from src.premium.schemas import PremiumRecipient
from src.redis import Redis
from src.schemas import BaseRecipient
from src.stars.schemas import StarsRecipient


@pytest.fixture
def redis_mock() -> MagicMock:
    mock = MagicMock(spec=Redis)
    mock.get = AsyncMock()
    mock.set = AsyncMock()

    return mock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "recipient_data",
    [
        StarsRecipient(
            recipient="SomeRec1pient_Hash",
            photo='<img src="https://some-domain.com/image.png"',
            name="Gigg Rigg",
        ),
        None,
    ],
)
async def test_stars_returns_right_data_from_cache(
    recipient_data: BaseRecipient | None, redis_mock: MagicMock
) -> None:
    redis_mock.get = AsyncMock(
        return_value=recipient_data.model_dump_json() if recipient_data else None
    )

    data = await stars_recipient_cache.get(redis=redis_mock, username="someUs3rNam3")

    redis_mock.get.assert_awaited_once_with(
        name=f"{stars_recipient_cache.caching_key}:someUs3rNam3"
    )

    assert data == (
        BaseRecipient(**recipient_data.model_dump()) if recipient_data else None
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "recipient_data",
    [
        PremiumRecipient(
            recipient="DiffrentRec1pient_Hash",
            photo='<img src="https://otherdomain.com/somefile/path.jpg"',
            name="19991",
        ),
        None,
    ],
)
async def test_premium_returns_right_data_from_cache(
    recipient_data: BaseRecipient | None, redis_mock: MagicMock
) -> None:
    redis_mock.get = AsyncMock(
        return_value=recipient_data.model_dump_json() if recipient_data else None
    )

    data = await premium_recipient_cache.get(redis=redis_mock, username="someUs3rNam3")

    assert data == (
        BaseRecipient(**recipient_data.model_dump()) if recipient_data else None
    )
    redis_mock.get.assert_awaited_once_with(
        name=f"{premium_recipient_cache.caching_key}:someUs3rNam3"
    )


@pytest.mark.asyncio
async def test_sets_stars_recipient_with_right_data_expiration(
    redis_mock: MagicMock,
) -> None:
    stars_recipient = StarsRecipient(
        recipient="SomeRec1pient_Hash",
        photo='<img src="https://some-domain.com"',
        name="Gigg Rigg",
    )

    await stars_recipient_cache.set(
        redis=redis_mock,
        username="my_username1337",
        recipient=stars_recipient,
    )

    redis_mock.set.assert_awaited_once_with(
        name=f"{stars_recipient_cache.caching_key}:my_username1337",
        value=stars_recipient.model_dump_json(),
        ex=settings.RECIPIENT_CACHE_TIME,
    )


@pytest.mark.asyncio
async def test_sets_premium_recipient_with_right_data_and_expiration(
    redis_mock: MagicMock,
) -> None:
    premium_recipient = PremiumRecipient(
        recipient="iK1AXAHS9Y1zluqw6gO2K245g61CdyrvCZO0gpBTPzUcuk725VEM28Tk631cc780",
        photo='<img src="https://some-domain.com/some-image.webp"',
        name="✨",  # test emoji caching aswell.
    )

    await premium_recipient_cache.set(
        redis=redis_mock,
        username="devsynca",
        recipient=premium_recipient,
    )

    redis_mock.set.assert_awaited_once_with(
        name=f"{premium_recipient_cache.caching_key}:devsynca",
        value=premium_recipient.model_dump_json(),
        ex=settings.RECIPIENT_CACHE_TIME,
    )


@pytest.mark.asyncio
async def test_sets_stars_recipient_and_gets(redis: Redis) -> None:
    stars_recipient = StarsRecipient(
        recipient="iK1AXAHS9Y1zluqw6gO2K245g61CdyrvCZO0gpBTPzUcuk725VEM28Tk631cc780",
        photo='<img src="https://some-domain.com/and/some/image.png"',
        name="🕳️riggie",
    )

    await stars_recipient_cache.set(
        redis=redis,
        username="monk",
        recipient=stars_recipient,
    )

    got_recipient = await stars_recipient_cache.get(redis=redis, username="monk")

    assert BaseRecipient(**stars_recipient.model_dump()) == got_recipient
