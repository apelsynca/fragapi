from contextlib import asynccontextmanager
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from ton_core import begin_cell, cell_to_b64

from src.enums import BulkPurchaseStatus
from src.integrations.fragment.exceptions import FragmentAPIUsersNotFound
from src.integrations.fragment.types import BuyLink, FoundRecipientData, RecipientData
from src.models import User
from src.postgres import AsyncSession
from src.redis import Redis
from src.stars.schemas import BulkBuyStars, BuyStars
from src.stars.service import stars as stars_service
from src.stars.tasks import stars_bulk_purchase_process
from tests.fixtures.random_objects import get_tc_transaction
from tests.fixtures.ton_connect import get_valid_tc_msg
from tests.fixtures.worker import FakeWalletManager

FOUND = RecipientData(
    ok=True,
    found=FoundRecipientData(myself=False, recipient="Mt", photo="", name="Name"),
)


class ImmediateGate:
    async def assert_owned(self):
        pass

    async def reserve_seqno(self, seqno):
        pass

    @asynccontextmanager
    async def attempt(self):
        yield


@pytest.fixture(autouse=True)
def enqueue_task_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.transaction.tasks.enqueue_task")


def _buy_link(i: int) -> BuyLink:
    msg = get_valid_tc_msg(amount=1)
    # Distinct payloads, message hashes are unique.
    msg.payload = cell_to_b64(begin_cell().store_uint(i, 32).end_cell())
    return BuyLink(transaction=get_tc_transaction(messages=[msg]), ok=True)


async def _run(session, bulk, fragment, redis, manager) -> None:
    await stars_bulk_purchase_process(
        bulk_purchase_id=bulk.id,
        session=session,
        fragment=fragment,
        redis=redis,
        wallet_manager=manager,
        send_gate=ImmediateGate(),
    )


async def _create(session: AsyncSession, user: User, *usernames: str):
    bulk = await stars_service.create_bulk(
        session=session,
        user=user,
        data=BulkBuyStars(items=[BuyStars(username=u, quantity=50) for u in usernames]),
    )
    await session.commit()
    return bulk


@pytest.mark.asyncio
async def test_bulk_purchase_charges_and_sends_once(
    session: AsyncSession, user: User, fragment: MagicMock, redis: Redis
) -> None:
    user.balance = 100
    fragment.search_stars_recipient.side_effect = [
        FOUND,
        FragmentAPIUsersNotFound(),
        FOUND,
    ]
    fragment.get_buy_stars_link.side_effect = [_buy_link(1), _buy_link(2)]
    bulk = await _create(session, user, "one_user", "missing_user", "two_user")
    manager = FakeWalletManager()

    await _run(session, bulk, fragment, redis, manager)
    balance_after = user.balance
    await _run(session, bulk, fragment, redis, manager)  # redelivered job

    assert bulk.status == BulkPurchaseStatus.done
    assert balance_after < 100
    assert user.balance == balance_after
    manager.wallet.client.send_message.assert_awaited_once()
    assert len(manager.wallet.build_external_message.call_args.args[0]) == 2
    one, missing, two = stars_service.bulk_response(bulk).items
    assert one.result is not None
    assert two.result is not None
    assert missing.error == "User is not found"


@pytest.mark.asyncio
async def test_bulk_purchase_retry_after_send_failure_does_not_charge_again(
    session: AsyncSession, user: User, fragment: MagicMock, redis: Redis
) -> None:
    user.balance = 100
    fragment.search_stars_recipient.return_value = FOUND
    fragment.get_buy_stars_link.side_effect = [_buy_link(1)]
    bulk = await _create(session, user, "one_user")
    manager = FakeWalletManager()
    manager.wallet.client.send_message.side_effect = TimeoutError("response lost")

    with pytest.raises(TimeoutError):
        await _run(session, bulk, fragment, redis, manager)
    assert bulk.status == BulkPurchaseStatus.charged
    balance_after = user.balance

    await _run(session, bulk, fragment, redis, manager)

    assert bulk.status == BulkPurchaseStatus.done
    assert user.balance == balance_after
    fragment.get_buy_stars_link.assert_called_once()
    # Possibly sent already, so it is never broadcast a second time.
    manager.wallet.client.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_bulk_purchase_with_every_item_failing_charges_and_sends_nothing(
    session: AsyncSession, user: User, fragment: MagicMock, redis: Redis
) -> None:
    user.balance = 100
    fragment.search_stars_recipient.side_effect = FragmentAPIUsersNotFound()
    bulk = await _create(session, user, "missing_user")
    manager = FakeWalletManager()

    await _run(session, bulk, fragment, redis, manager)

    assert bulk.status == BulkPurchaseStatus.done
    assert user.balance == 100
    manager.wallet.client.send_message.assert_not_awaited()
