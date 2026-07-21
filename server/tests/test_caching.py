from unittest.mock import AsyncMock, MagicMock

import pytest

from src.caching import premium_recipient_cache, stars_recipient_cache
from src.premium.schemas import PremiumRecipient
from src.redis import Redis
from src.schemas import BaseRecipient
from src.stars.schemas import StarsRecipient


@pytest.fixture
def redis_mock() -> MagicMock:
    return MagicMock(spec=Redis)


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


# @pytest.mark.asyncio
# async def test_sets_recipient_hash(redis_mock: MagicMock) -> None:
#     stars_recipient = StarsRecipient(
#         recipient="SomeRec1pient_Hash",
#         photo='<img src="https://some-domain.com"',
#         name="Gigg Rigg",
#     )
#
#     await stars_recipient_cache.set(
#         redis=redis_mock,
#         username="my_username1337",
#         recipient=stars_recipient,
#     )
#
#     redis_mock.set.assert_awaited_once_with(
#         name=f"{stars_recipient_cache.caching_key}:my_username1337",
#         value=stars_recipient.model_dump_json(),
#         ex=timedelta(minutes=10),
#     )
