from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import update

from src.caching import RecipientCache
from src.enums import BulkPurchaseStatus, TransactionReason
from src.exceptions import (
    BadRequest,
    FragError,
    InsufficientFunds,
    ResourceNotFound,
)
from src.integrations.fragment.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIError,
    FragmentAPINotAUser,
    FragmentAPIUsersNotFound,
    FragmentError,
)
from src.integrations.fragment.types import BuyLink, FoundRecipientData, RecipientData
from src.kit.ton_connect import TonConnectTransaction
from src.models import StarsBulkPurchase, User
from src.postgres import AsyncSession
from src.redis import Redis
from src.schemas import BaseRecipient
from src.stars.schemas import BulkBuyStars, BuyStars, StarsRecipient
from src.stars.service import FRAGMENT_UNAVAILABLE
from src.stars.service import stars as stars_service
from src.transaction.models import FTMetadata
from src.transaction.service import TransactionService
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction, create_transaction


@pytest.fixture(autouse=True)
def transaction_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.stars.service.transaction_service",
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
    fragment.search_stars_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="", name=""
        ),
    )
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )
    transaction = await create_ton_transaction(
        save_fixture,
        message_hash="vaid",
    )

    transaction_service.send_from_tc.return_value = await create_transaction(
        save_fixture, user=user, ton_transaction=transaction
    )

    await stars_service.buy(
        session=session,
        user=user,
        data=BuyStars(username="homocitrus", quantity=52),
        fragment=fragment,
        redis=redis,
    )

    transaction_service.send_from_tc.assert_called_once_with(
        session=session,
        tc_transaction=valid_tc_transaction,
        user=user,
        reason=TransactionReason.stars,
        metadata=FTMetadata(
            recipient="SomeMtDataXx", recipient_username="homocitrus", stars_amount=52
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
    fragment.search_stars_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="", name=""
        ),
    )
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=False
    )

    with pytest.raises(FragError):
        await stars_service.buy(
            session=session,
            user=user,
            data=BuyStars(username="homocitrus", quantity=52),
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
    fragment.search_stars_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True,
            recipient="SomeMtDataXx",
            photo='<img src="https://cdn.somestorage.com/somewhere/image.jpg" />',
            name="TheName",
        ),
    )
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )

    ton_transaction = await create_ton_transaction(
        save_fixture,
        message_hash="myhash",
    )
    frag_trans = await create_transaction(
        save_fixture, user=user, ton_transaction=ton_transaction
    )

    transaction_service.send_from_tc.return_value = frag_trans

    stars_buy_response = await stars_service.buy(
        session=session,
        user=user,
        data=BuyStars(username="homocitrus", quantity=52),
        fragment=fragment,
        redis=redis,
    )

    assert stars_buy_response.message_hash == "myhash"
    assert stars_buy_response.transaction_id == frag_trans.id
    assert (
        stars_buy_response.avatar_url
        == "https://cdn.somestorage.com/somewhere/image.jpg"
    )
    assert stars_buy_response.name == "TheName"
    assert stars_buy_response.amount is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("username", ["apelsynca", "SyncaViA"])
async def test_get_recipient_raises_if_fragment_not_found(
    fragment: MagicMock, username: str, redis: Redis
) -> None:
    fragment.search_stars_recipient.side_effect = FragmentAPIUsersNotFound()
    with pytest.raises(ResourceNotFound):
        await stars_service.get_recipient(
            fragment=fragment, username=username, redis=redis
        )


@pytest.mark.asyncio
async def test_get_recipient_raises_not_found_if_fragment_not_a_user(
    fragment: MagicMock, redis: Redis
) -> None:
    fragment.search_stars_recipient.side_effect = FragmentAPINotAUser()
    with pytest.raises(ResourceNotFound):
        await stars_service.get_recipient(
            fragment=fragment, username="my_username", redis=redis
        )


@pytest.mark.asyncio
async def test_get_recipient_raises_app_error_if_fragment_api_error(
    fragment: MagicMock, redis: Redis
) -> None:
    fragment.search_stars_recipient.side_effect = FragmentAPIError()
    with pytest.raises(BadRequest):
        await stars_service.get_recipient(
            fragment=fragment, username="Guser007", redis=redis
        )


@pytest.mark.asyncio
async def test_get_recipient_raises_app_error_if_fragment_access_denied(
    fragment: MagicMock, redis: Redis
) -> None:
    fragment.search_stars_recipient.side_effect = FragmentAPIAccessDenied()
    with pytest.raises(FragError):
        await stars_service.get_recipient(
            fragment=fragment, username="My_usernamik123", redis=redis
        )


@pytest.mark.asyncio
async def test_get_recipient_returns_cached_when_exists(
    fragment: MagicMock, redis: Redis, mocker: MockerFixture
) -> None:
    fragment.search_stars_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True,
            recipient="SomeRecipientHashOrShi",
            photo='<img src="https://somePhotoUrl" />',
            name="NewNameThatWasChanged",
        ),
    )

    recipient_cache_mock = mocker.patch(
        "src.stars.service.stars_recipient_cache", spec=RecipientCache
    )
    recipient_cache_mock.get.return_value = BaseRecipient(
        name="CachedName",
        photo='<img src="https://cached-url.com/abc" />',
        recipient="doesNotMatter",
    )

    recipient_data = await stars_service.get_recipient(
        fragment=fragment, username="userUsernamik", redis=redis
    )

    recipient_cache_mock.get.assert_awaited_once_with(
        redis=redis, username="userUsernamik"
    )

    fragment.search_stars_recipient.assert_not_called()
    assert recipient_data.name == "CachedName"
    assert recipient_data.photo == '<img src="https://cached-url.com/abc" />'
    assert recipient_data.recipient == "doesNotMatter"
    assert recipient_data.avatar_url == "https://cached-url.com/abc"


@pytest.mark.asyncio
async def test_get_recipient_fetches_when_uncached(
    fragment: MagicMock, redis: Redis, mocker: MockerFixture
) -> None:
    fragment.search_stars_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True,
            recipient="Found-Some_Recipient8123Hash",
            photo='<img src="https://somestupid.domain.com/5123akakakakasdasd.jpg" />',
            name="Name NonCached",
        ),
    )

    recipient_cache_mock = mocker.patch(
        "src.stars.service.stars_recipient_cache", spec=RecipientCache
    )
    recipient_cache_mock.get.return_value = None

    recipient_data = await stars_service.get_recipient(
        fragment=fragment, username="some_user91", redis=redis
    )

    fragment.search_stars_recipient.assert_called_once()
    recipient_cache_mock.get.assert_awaited_once_with(
        redis=redis, username="some_user91"
    )

    expected_recipient_data = StarsRecipient(
        name="Name NonCached",
        photo='<img src="https://somestupid.domain.com/5123akakakakasdasd.jpg" />',
        recipient="Found-Some_Recipient8123Hash",
    )
    assert recipient_data == expected_recipient_data
    recipient_cache_mock.set.assert_awaited_once_with(
        redis=redis, recipient=expected_recipient_data, username="some_user91"
    )


FOUND = RecipientData(
    ok=True,
    found=FoundRecipientData(
        myself=False, recipient="SomeMtDataXx", photo="", name="Name"
    ),
)


async def _bulk(session: AsyncSession, user: User, *usernames: str):
    bulk = await stars_service.create_bulk(
        session=session,
        user=user,
        data=BulkBuyStars(items=[BuyStars(username=u, quantity=50) for u in usernames]),
    )
    await session.flush()
    return bulk


@pytest.mark.asyncio
async def test_charge_bulk_skips_failed_items_and_charges_the_rest(
    save_fixture: SaveFixture,
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
    transaction_service: MagicMock,
    redis: Redis,
) -> None:
    fragment.search_stars_recipient.side_effect = [
        FOUND,
        FragmentAPIUsersNotFound(),
        FOUND,
    ]
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )
    transaction = await create_transaction(
        save_fixture,
        user=user,
        ton_transaction=await create_ton_transaction(save_fixture, message_hash="h"),
    )
    transaction_service.charge_bulk_from_tc.return_value = [
        transaction,
        InsufficientFunds(),
    ]
    bulk = await _bulk(session, user, "@first_user", "missing_user", "third_user")

    await stars_service.charge_bulk(
        session=session, bulk=bulk, fragment=fragment, redis=redis
    )

    purchases = transaction_service.charge_bulk_from_tc.call_args.kwargs["purchases"]
    assert [metadata.recipient_username for _, metadata in purchases] == [
        "first_user",
        "third_user",
    ]
    assert bulk.status == BulkPurchaseStatus.charged
    first, missing, third = stars_service.bulk_response(bulk).items
    assert first.error is None
    assert first.result is not None
    assert first.result.transaction_id == transaction.id
    assert missing.result is None
    assert missing.error == "User is not found"
    assert third.result is None
    assert third.error == "Insufficient funds"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fragment_failure",
    [FragmentError("Status - 429"), FragmentAPIAccessDenied("access denied")],
)
async def test_charge_bulk_stops_asking_fragment_when_it_fails(
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
    transaction_service: MagicMock,
    redis: Redis,
    fragment_failure: Exception,
) -> None:
    fragment.search_stars_recipient.side_effect = [FOUND, fragment_failure]
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )
    transaction_service.charge_bulk_from_tc.return_value = [InsufficientFunds()]
    bulk = await _bulk(session, user, "first_user", "second_user", "third_user")

    await stars_service.charge_bulk(
        session=session, bulk=bulk, fragment=fragment, redis=redis
    )

    # Third user is never asked for, the first one still goes to charging.
    assert fragment.search_stars_recipient.call_count == 2
    purchases = transaction_service.charge_bulk_from_tc.call_args.kwargs["purchases"]
    assert [metadata.recipient_username for _, metadata in purchases] == ["first_user"]
    _, second, third = stars_service.bulk_response(bulk).items
    assert second.error == FRAGMENT_UNAVAILABLE
    assert third.error == FRAGMENT_UNAVAILABLE


@pytest.mark.asyncio
async def test_charge_bulk_does_not_charge_a_batch_charged_meanwhile(
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
    transaction_service: MagicMock,
    redis: Redis,
) -> None:
    fragment.search_stars_recipient.return_value = FOUND
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )
    bulk = await _bulk(session, user, "first_user")

    async def charged_by_another_delivery(**_):
        await session.execute(
            update(StarsBulkPurchase)
            .where(StarsBulkPurchase.id == bulk.id)
            .values(status=BulkPurchaseStatus.charged)
        )
        return FOUND

    fragment.search_stars_recipient.side_effect = charged_by_another_delivery

    await stars_service.charge_bulk(
        session=session, bulk=bulk, fragment=fragment, redis=redis
    )

    transaction_service.charge_bulk_from_tc.assert_not_called()


@pytest.mark.asyncio
async def test_get_bulk_hides_other_users_batches(
    session: AsyncSession, user: User, user_second: User
) -> None:
    bulk = await _bulk(session, user, "first_user")

    assert await stars_service.get_bulk(session=session, user=user, id=bulk.id) == bulk
    with pytest.raises(ResourceNotFound):
        await stars_service.get_bulk(session=session, user=user_second, id=bulk.id)
