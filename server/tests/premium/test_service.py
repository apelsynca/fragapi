from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.caching import RecipientCache
from src.enums import PremiumMonths, TransactionReason
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.integrations.fragment.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIError,
    FragmentAPINotAUser,
    FragmentAPIUsersNotFound,
)
from src.integrations.fragment.types import BuyLink, FoundRecipientData, RecipientData
from src.kit.ton_connect import TonConnectTransaction
from src.models import User
from src.postgres import AsyncSession
from src.premium.schemas import BuyPremium, PremiumRecipient
from src.premium.service import premium as premium_service
from src.redis import Redis
from src.schemas import BaseRecipient
from src.transaction.models import FTMetadata
from src.transaction.service import TransactionService
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction, create_transaction


@pytest.fixture(autouse=True)
def transaction_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.premium.service.transaction_service",
        spec=TransactionService,
    )


@pytest.mark.asyncio
async def test_buy_calls_frag_service_buy_from_tc(
    save_fixture: SaveFixture,
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
    transaction_service: MagicMock,
    redis: Redis,
) -> None:
    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="", name=""
        ),
    )
    fragment.get_gift_premium_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )
    ton_transaction = await create_ton_transaction(
        save_fixture,
        message_hash="vaid",
    )

    transaction_service.send_from_tc.return_value = await create_transaction(
        save_fixture, user=user, ton_transaction=ton_transaction
    )

    await premium_service.buy(
        session=session,
        user=user,
        data=BuyPremium(username="homocitrus", months=PremiumMonths.SIX_MONTHS),
        fragment=fragment,
        redis=redis,
    )

    transaction_service.send_from_tc.assert_called_once_with(
        session=session,
        tc_transaction=valid_tc_transaction,
        user=user,
        reason=TransactionReason.premium,
        metadata=FTMetadata(
            recipient="SomeMtDataXx", recipient_username="homocitrus", premium_months=6
        ),
    )


@pytest.mark.asyncio
async def test_buy_raises_if_link_is_false(
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
    redis: Redis,
) -> None:
    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="", name=""
        ),
    )
    fragment.get_gift_premium_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=False
    )

    with pytest.raises(FragError):
        await premium_service.buy(
            session=session,
            user=user,
            data=BuyPremium(username="homocitrus", months=PremiumMonths.YEAR),
            fragment=fragment,
            redis=redis,
        )


@pytest.mark.asyncio
async def test_buy_returns_good(
    save_fixture: SaveFixture,
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
    transaction_service: MagicMock,
    redis: Redis,
) -> None:
    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="the photo", name="TheName"
        ),
    )
    fragment.get_gift_premium_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )

    ton_transaction = await create_ton_transaction(
        save_fixture,
        message_hash="myhash",
    )
    transaction = await create_transaction(
        save_fixture, user=user, ton_transaction=ton_transaction
    )

    transaction_service.send_from_tc.return_value = transaction

    # When
    prem_buy_response = await premium_service.buy(
        session=session,
        user=user,
        data=BuyPremium(username="homocitrus", months=PremiumMonths.THREE_MONTHS),
        fragment=fragment,
        redis=redis,
    )

    assert prem_buy_response.message_hash == "myhash"
    assert prem_buy_response.transaction_id == transaction.id
    assert prem_buy_response.photo == "the photo"
    assert prem_buy_response.name == "TheName"
    assert prem_buy_response.amount is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("username", ["someusername", "literrally_Anyusername"])
async def test_get_recipient_raises_not_found_if_fragment_not_found(
    fragment: MagicMock, username: str, redis: Redis
) -> None:
    fragment.search_premium_gift_recipient.side_effect = FragmentAPIUsersNotFound()
    with pytest.raises(ResourceNotFound):
        await premium_service.get_recipient(
            fragment=fragment, username=username, redis=redis
        )


@pytest.mark.asyncio
async def test_get_recipient_raises_not_found_if_fragment_not_a_user(
    fragment: MagicMock, redis: Redis
) -> None:
    fragment.search_premium_gift_recipient.side_effect = FragmentAPINotAUser()
    with pytest.raises(ResourceNotFound):
        await premium_service.get_recipient(
            fragment=fragment, username="my_username", redis=redis
        )


@pytest.mark.asyncio
async def test_get_recipient_raises_app_error_if_fragment_api_error(
    fragment: MagicMock, redis: Redis
) -> None:
    fragment.search_premium_gift_recipient.side_effect = FragmentAPIError()
    with pytest.raises(BadRequest):
        await premium_service.get_recipient(
            fragment=fragment, username="Guser007", redis=redis
        )


@pytest.mark.asyncio
async def test_get_recipient_raises_app_error_if_fragment_access_denied(
    fragment: MagicMock, redis: Redis
) -> None:
    fragment.search_premium_gift_recipient.side_effect = FragmentAPIAccessDenied()
    with pytest.raises(FragError):
        await premium_service.get_recipient(
            fragment=fragment, username="My_usernamik123", redis=redis
        )


@pytest.mark.asyncio
async def test_get_recipient_returns_cached_when_exists(
    fragment: MagicMock, redis: Redis, mocker: MockerFixture
) -> None:
    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True,
            recipient="SomeRecipientHashOrShi",
            photo='<img src="https://somePhotoUrl" />',
            name="NewNameThatWasChanged",
        ),
    )

    recipient_cache_mock = mocker.patch(
        "src.premium.service.premium_recipient_cache", spec=RecipientCache
    )
    recipient_cache_mock.get.return_value = BaseRecipient(
        name="CachedName",
        photo='<img src="https://cached-url.com/abc" />',
        recipient="doesNotMatter",
    )

    recipient_data = await premium_service.get_recipient(
        fragment=fragment, username="userUsernamik", redis=redis
    )

    recipient_cache_mock.get.assert_awaited_once_with(
        redis=redis, username="userUsernamik"
    )

    fragment.search_premium_gift_recipient.assert_not_called()
    assert recipient_data.name == "CachedName"
    assert recipient_data.photo == '<img src="https://cached-url.com/abc" />'
    assert recipient_data.recipient == "doesNotMatter"
    assert recipient_data.avatar_url == "https://cached-url.com/abc"


@pytest.mark.asyncio
async def test_get_recipient_fetches_when_uncached(
    fragment: MagicMock, redis: Redis, mocker: MockerFixture
) -> None:
    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True,
            recipient="Found-Some_Recipient8123Hash",
            photo='<img src="https://somestupid.domain.com/5123akakakakasdasd.jpg" />',
            name="Name NonCached",
        ),
    )

    recipient_cache_mock = mocker.patch(
        "src.premium.service.premium_recipient_cache", spec=RecipientCache
    )
    recipient_cache_mock.get.return_value = None

    recipient_data = await premium_service.get_recipient(
        fragment=fragment, username="some_user91", redis=redis
    )

    fragment.search_premium_gift_recipient.assert_called_once()
    recipient_cache_mock.get.assert_awaited_once_with(
        redis=redis, username="some_user91"
    )

    expected_recipient_data = PremiumRecipient(
        name="Name NonCached",
        photo='<img src="https://somestupid.domain.com/5123akakakakasdasd.jpg" />',
        recipient="Found-Some_Recipient8123Hash",
    )
    assert recipient_data == expected_recipient_data
    recipient_cache_mock.set.assert_awaited_once_with(
        redis=redis, recipient=expected_recipient_data, username="some_user91"
    )
