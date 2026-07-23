import random
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from freezegun import freeze_time
from pytest_mock import MockerFixture
from ton_core import Address, Cell, WalletV5Params, to_nano
from tonutils.contracts import WalletV5R1

from src.enums import TransactionReason
from src.exceptions import BadRequest, FragRequestValidationError, ResourceNotFound
from src.fee import approx_before_fee
from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from src.kit.utils import utc_now
from src.models import Transaction, User
from src.models.deposits import Deposit, DepositStatus
from src.postgres import AsyncSession
from src.telegram_log.tasks import admin_telegram_log_send
from src.transaction.tasks import (
    DAILY_LOG_TEXT,
    fragment_transaction_process,
    transactions_log_daily_stats,
)
from src.wallet.manager import WalletManager
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import (
    create_ton_transaction,
    create_transaction,
    rstr,
)
from tests.fixtures.worker import FakeWalletManager


@pytest.fixture
def enqueue_task_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.transaction.tasks.enqueue_task")


@pytest_asyncio.fixture
async def valid_transaction(
    save_fixture: SaveFixture, valid_tc_transaction_hash: str, user: User
) -> Transaction:
    transaction = await create_ton_transaction(
        save_fixture,
        message_hash=valid_tc_transaction_hash,
    )
    return await create_transaction(
        save_fixture, user=user, ton_transaction=transaction
    )


@pytest.mark.asyncio
async def test_process_transaction_raises_if_not_found(
    valid_tc_transaction: TonConnectTransaction,
    session: AsyncSession,
    wallet_manager: WalletManager,
) -> None:
    with pytest.raises(ResourceNotFound):
        await fragment_transaction_process(
            transaction_id=uuid.uuid4(),
            tc_transaction=valid_tc_transaction,
            session=session,
            wallet_manager=wallet_manager,
        )


@pytest.mark.asyncio
async def test_process_raises_if_transaction_msg_hash_differ_from_tc_transaction(
    save_fixture: SaveFixture,
    valid_tc_transaction: TonConnectTransaction,
    user: User,
    session: AsyncSession,
    wallet_manager: WalletManager,
) -> None:
    transaction = await create_ton_transaction(
        save_fixture, message_hash="completely-wrong-hash"
    )
    frag_trans = await create_transaction(
        save_fixture, user=user, ton_transaction=transaction
    )

    with pytest.raises(BadRequest):
        await fragment_transaction_process(
            transaction_id=frag_trans.id,
            tc_transaction=valid_tc_transaction,
            session=session,
            wallet_manager=wallet_manager,
        )


@pytest.mark.asyncio
async def test_process_raises_if_tc_msg_len_diff(
    valid_tc_transaction: TonConnectTransaction,
    valid_transaction: Transaction,
    session: AsyncSession,
    wallet_manager: WalletManager,
) -> None:
    valid_tc_transaction.messages.append(
        TonConnectMessage(address="", amount=0, payload="")
    )

    with pytest.raises(FragRequestValidationError):
        await fragment_transaction_process(
            transaction_id=valid_transaction.id,
            tc_transaction=valid_tc_transaction,
            session=session,
            wallet_manager=wallet_manager,
        )


@pytest.mark.asyncio
async def test_process_calls_transfer(
    valid_tc_transaction: TonConnectTransaction,
    valid_transaction: Transaction,
    session: AsyncSession,
) -> None:
    tc_msg = valid_tc_transaction.messages[0]
    assert tc_msg.payload is not None

    wallet_manager_mock = MagicMock(spec=WalletManager)
    wallet_mock = MagicMock(spec=WalletV5R1)
    wallet_mock.balance = to_nano(25.2)

    external_message_mock = MagicMock()
    external_message_mock.normalized_hash = "anyhash"
    wallet_mock.transfer.return_value = external_message_mock

    wallet_manager_mock.get_wallet_for_amount.return_value = wallet_mock

    # When
    await fragment_transaction_process(
        transaction_id=valid_transaction.id,
        tc_transaction=valid_tc_transaction,
        session=session,
        wallet_manager=wallet_manager_mock,
    )

    # Then
    padded_payload = tc_msg.payload + "=" * (-len(tc_msg.payload) % 4)
    body = Cell.one_from_boc(padded_payload)

    wallet_mock.transfer.assert_called_once_with(
        destination=Address(tc_msg.address),
        body=body,
        amount=tc_msg.amount,
        params=WalletV5Params(
            valid_until=int(valid_tc_transaction.valid_until.timestamp()) + 10
        ),
    )


@pytest.mark.asyncio
async def test_process_calls_validate_transaction(
    valid_tc_transaction: TonConnectTransaction,
    valid_transaction: Transaction,
    mocker: MockerFixture,
    session: AsyncSession,
) -> None:
    wallet_manager = FakeWalletManager()
    mock = mocker.patch(
        "src.transaction.tasks.validate_tc_transaction",
        side_effect=FragRequestValidationError([]),
    )

    with pytest.raises(FragRequestValidationError):
        await fragment_transaction_process(
            transaction_id=valid_transaction.id,
            tc_transaction=valid_tc_transaction,
            session=session,
            wallet_manager=wallet_manager,
        )

    mock.assert_called_once_with(tc_transaction=valid_tc_transaction)
    wallet_manager.wallet.transfer.assert_not_called()


@pytest.mark.asyncio
async def test_process_sets_hash(
    valid_tc_transaction: TonConnectTransaction,
    valid_transaction: Transaction,
    session: AsyncSession,
) -> None:
    wallet_manager = FakeWalletManager()

    assert valid_transaction.ton_transaction.hash is None

    wallet_mock = MagicMock(spec=WalletV5R1)
    wallet_mock.normalized_hash = "MyHash-ThatIt_Sh0uldSet"
    wallet_manager.wallet.transfer.return_value = wallet_mock

    await fragment_transaction_process(
        transaction_id=valid_transaction.id,
        tc_transaction=valid_tc_transaction,
        session=session,
        wallet_manager=wallet_manager,
    )

    assert valid_transaction.ton_transaction.hash == "MyHash-ThatIt_Sh0uldSet"


async def create_user(save_fixture: SaveFixture, *, balance: float = 0) -> User:
    user = User(first_name=rstr("Mock"), username=rstr("test_"), balance=balance)
    await save_fixture(user)
    return user


# only for dep test
async def create_deposit(
    save_fixture: SaveFixture,
    user: User,
    amount: float,
    created_at: datetime,
    *,
    completed: bool = True,
) -> Deposit:
    deposit = Deposit(
        user=user,
        amount=amount,
        hash=rstr("mock_hash"),
        ton_transaction=None,
        status=DepositStatus.completed if completed else DepositStatus.pending,
        created_at=created_at,
    )
    await save_fixture(deposit)
    return deposit


async def create_transaction_with_ton_transaction(
    save_fixture: SaveFixture,
    user: User,
    *,
    amount: float | None = None,
    created_at: datetime | None = None,
) -> Transaction:
    # message_hash valid?
    transaction = await create_ton_transaction(save_fixture, amount=amount)

    frag_t = Transaction(
        user=user,
        recipient=rstr("recipient"),
        recipient_username=rstr("username"),
        amount=amount if amount is not None else random.randint(1, 250) / 100,
        ton_transaction=transaction,
        reason=TransactionReason.stars,
        created_at=utc_now() if created_at is None else created_at,
    )
    await save_fixture(frag_t)

    return frag_t


@freeze_time("2026-02-06")
@pytest.mark.asyncio
async def test_log_daily_stats_right_text(
    save_fixture: SaveFixture,
    enqueue_task_mock: MagicMock,
    user: User,
    user_second: User,
    session: AsyncSession,
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    await create_transaction_with_ton_transaction(save_fixture, user, amount=5.25)
    await create_transaction_with_ton_transaction(
        save_fixture, user, amount=5.25, created_at=yesterday_dt
    )
    await create_transaction_with_ton_transaction(
        save_fixture,
        user_second,
        amount=2.50,
        created_at=yesterday_dt - timedelta(minutes=52),
    )
    await create_transaction_with_ton_transaction(
        save_fixture,
        user_second,
        amount=3.25,
        created_at=yesterday_dt - timedelta(days=1),
    )

    await transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        admin_telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=0,
            volume=7.75,
            raw_commission_amount=approx_before_fee(7.75),
            transactions_count=2,
            transactions_unique_users=2,
            new_users_count=0,
            deposits_count=0,
            deposits_amount=0,
            deposit_requests_count=0,
            users_total_count=2,
        ),
        with_notification=False,
    )


@freeze_time("2026-12-12")
@pytest.mark.asyncio
async def test_log_empty_text(
    enqueue_task_mock: MagicMock, session: AsyncSession
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    await transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        admin_telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=0,
            volume=0,
            raw_commission_amount=0,
            transactions_count=0,
            transactions_unique_users=0,
            new_users_count=0,
            deposits_count=0,
            deposits_amount=0,
            deposit_requests_count=0,
            users_total_count=0,
        ),
        with_notification=False,
    )


@pytest.mark.asyncio
async def test_log_right_unique_users_and_total_balance(
    save_fixture: SaveFixture, enqueue_task_mock: MagicMock, session: AsyncSession
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    users = [
        await create_user(save_fixture, balance=3),
        await create_user(save_fixture, balance=1.07),
        await create_user(save_fixture, balance=1.05),
    ]

    for user in users:
        await create_transaction_with_ton_transaction(
            save_fixture, user, amount=5, created_at=yesterday_dt
        )
        await create_transaction_with_ton_transaction(
            save_fixture, user, amount=3, created_at=yesterday_dt
        )

    await transactions_log_daily_stats(session)

    users_count = len(users)
    enqueue_task_mock.assert_called_once_with(
        admin_telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=5.12,
            volume=8 * users_count,
            raw_commission_amount=approx_before_fee(8 * users_count),
            transactions_count=users_count * 2,
            transactions_unique_users=users_count,
            new_users_count=0,
            deposits_count=0,
            deposits_amount=0,
            deposit_requests_count=0,
            users_total_count=3,
        ),
        with_notification=False,
    )


@pytest.mark.asyncio
async def test_log_right_new_users(
    save_fixture: SaveFixture, enqueue_task_mock: MagicMock, session: AsyncSession
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    for _ in range(3):  # create unique users
        user = User(
            first_name=rstr("Mock"), username=rstr("test_"), created_at=yesterday_dt
        )
        await save_fixture(user)

    await transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        admin_telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=0,
            volume=0,
            raw_commission_amount=0,
            transactions_count=0,
            transactions_unique_users=0,
            new_users_count=3,
            deposits_count=0,
            deposits_amount=0,
            deposit_requests_count=0,
            users_total_count=3,
        ),
        with_notification=False,
    )


@pytest.mark.asyncio
async def test_log_right_new_deposits(
    save_fixture: SaveFixture,
    enqueue_task_mock: MagicMock,
    session: AsyncSession,
) -> None:
    yesterday_dt = utc_now() - timedelta(days=1)

    users = [
        User(first_name=rstr("mockName"), username="gennie", created_at=yesterday_dt),
        User(first_name=rstr("mockName"), username="bynnie", created_at=yesterday_dt),
        User(first_name=rstr("mockName"), username="vinnie", created_at=yesterday_dt),
    ]

    await create_deposit(
        save_fixture, user=users[0], amount=5.25, created_at=yesterday_dt
    )
    await create_deposit(save_fixture, user=users[0], amount=1.85, created_at=utc_now())
    await create_deposit(save_fixture, user=users[2], amount=3, created_at=yesterday_dt)
    await create_deposit(save_fixture, user=users[1], amount=1.11, created_at=utc_now())
    await create_deposit(
        save_fixture,
        user=users[1],
        amount=3.22,
        created_at=yesterday_dt,
        completed=False,
    )

    for user in users:
        await save_fixture(user)

    await transactions_log_daily_stats(session)

    enqueue_task_mock.assert_called_once_with(
        admin_telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_dt.date().strftime("%m-%d"),
            total_balance=0,
            volume=0,
            raw_commission_amount=0,
            transactions_count=0,
            transactions_unique_users=0,
            new_users_count=3,
            deposits_count=2,
            deposits_amount=8.25,
            deposit_requests_count=3,
            users_total_count=3,
        ),
        with_notification=False,
    )
