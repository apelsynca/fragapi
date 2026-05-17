import uuid
from unittest.mock import ANY, MagicMock

import pytest
from pytest_mock import MockerFixture
from ton_core import to_nano

from src.bot.logs_sender import TelegramLogSender
from src.config import settings
from src.exceptions import BadRequest, ResourceNotFound
from src.fragment_transaction.tasks import (
    process_fragment_transaction,
    send_telegram_log,
)
from src.integrations.ton_wallet.manager import WalletManager
from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from src.models import Transaction, User
from src.wallet.service import WalletService
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import (
    create_fragment_transaction,
    create_transaction,
    get_tc_transaction,
    rstr,
)


@pytest.fixture(autouse=True)
def wallet_manager_mock(mocker: MockerFixture) -> MagicMock:
    m = mocker.patch(
        "src.fragment_transaction.tasks.wallet_manager", MagicMock(spec=WalletManager)
    )

    return m


@pytest.fixture(autouse=True)
def wallet_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.fragment_transaction.tasks.wallet_service", spec=WalletService
    )


@pytest.mark.asyncio
async def test_process_transaction_raises_if_not_found(
    tc_transaction: TonConnectTransaction,
) -> None:
    with pytest.raises(ResourceNotFound):
        await process_fragment_transaction(
            fragment_transaction_id=uuid.uuid4(), tc_transaction=tc_transaction
        )


@pytest.mark.asyncio
async def test_process_raises_if_transaction_msg_hash_differ_from_tc_transaction(
    save_fixture: SaveFixture, tc_transaction: TonConnectTransaction, user: User
) -> None:
    transaction = await create_transaction(
        save_fixture, message_hash=rstr("completely-wrong-hash")
    )
    frag_trans = await create_fragment_transaction(
        save_fixture, user=user, transaction=transaction
    )

    with pytest.raises(BadRequest):
        await process_fragment_transaction(
            fragment_transaction_id=frag_trans.id, tc_transaction=tc_transaction
        )


@pytest.mark.asyncio
async def test_process_raises_if_tc_msg_len_diff(
    save_fixture: SaveFixture, tc_transaction: TonConnectTransaction, user: User
) -> None:
    transaction = await create_transaction(
        save_fixture,
        message_hash="56d8110d9464839f5e3204de286e0ba1e24503c64b4c2f8d5874957aa2faa093",
    )
    frag_trans = await create_fragment_transaction(
        save_fixture, user=user, transaction=transaction
    )

    tc_transaction.messages.append(TonConnectMessage(address="", amount=0, payload=""))

    with pytest.raises(BadRequest):
        await process_fragment_transaction(
            fragment_transaction_id=frag_trans.id, tc_transaction=tc_transaction
        )


@pytest.mark.asyncio
async def test_process_calls_wallet_service_if_valid(
    save_fixture: SaveFixture,
    user: User,
    wallet_manager: MagicMock,
    wallet_service_mock: MagicMock,
) -> None:
    tc_transaction = get_tc_transaction(
        messages=[
            TonConnectMessage(
                address="UQANtyTiJuWgo5cTdrVlzpTzhYD3Heg3ssPoeAW2dM2v6nR1",
                amount=to_nano(5.25),
                payload="te6ccgEBAQEAJwAASgAAAAA1MCBUZWxlZ3JhbSBTdGFycyAKClJlZiN4Z01NbTM3bVY",
            )
        ]
    )

    transaction = await create_transaction(
        save_fixture,
        message_hash="04ab7405a2e4e5f6fd301505900598570737ec77fbeeeafea641bab5f0ef33eb",
    )
    frag_trans = await create_fragment_transaction(
        save_fixture, user=user, transaction=transaction
    )

    wallet_service_mock.send_from_tc_transaction.return_value = None

    await process_fragment_transaction(
        fragment_transaction_id=frag_trans.id,
        tc_transaction=tc_transaction,
    )

    wallet_service_mock.send_from_tc_transaction.assert_called_once_with(
        wallet_manager=wallet_manager, tc_transaction=tc_transaction
    )


@pytest.fixture
def telegram_log_sender(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.fragment_transaction.tasks.telegram_log_sender", spec=TelegramLogSender
    )


@pytest.mark.asyncio
async def test_sends_with_notification_if_more_than_cfgval_ton(
    save_fixture: SaveFixture,
    user: User,
    transaction: Transaction,
    telegram_log_sender: MagicMock,
) -> None:
    frag_transaction = await create_fragment_transaction(
        save_fixture,
        user=user,
        transaction=transaction,
        amount=settings.MIN_NON_SILENT_AMOUNT + 0.1,
    )

    await send_telegram_log(fragment_transaction_id=frag_transaction.id)

    telegram_log_sender.send.assert_called_once_with(text=ANY, with_notification=True)


@pytest.mark.asyncio
async def test_sends_without_notification_if_less_than_cfgval_ton(
    save_fixture: SaveFixture,
    user: User,
    transaction: Transaction,
    telegram_log_sender: MagicMock,
) -> None:
    frag_transaction = await create_fragment_transaction(
        save_fixture,
        user=user,
        transaction=transaction,
        amount=settings.MIN_NON_SILENT_AMOUNT - 0.1,
    )

    await send_telegram_log(fragment_transaction_id=frag_transaction.id)

    telegram_log_sender.send.assert_called_once_with(text=ANY, with_notification=False)
