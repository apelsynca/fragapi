from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from ton_core import to_amount

from src.bot import custom_emoji
from src.config import settings
from src.models import User
from src.models import Transaction
from src.telegram_log.tasks import admin_telegram_notification_send, telegram_log_send
from src.telegram_log.transaction import (
    ADMIN_TELEGRAM_BULK_TRANSACTION_NEXT_TEXT,
    ADMIN_TELEGRAM_BULK_TRANSACTION_TEXT,
    ADMIN_TELEGRAM_TRANSACTION_TEXT,
    ADMIN_TELEGRAM_TRANSACTION_TITLE_TEMPLATE,
    BULK_LINES_PER_MESSAGE,
    USER_TELEGRAM_BULK_LOG_TEXT,
    enqueue_bulk_transaction_admin_log_tasks,
    enqueue_bulk_transaction_telegram_log_tasks,
    enqueue_transaction_admin_log_task,
)
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction, create_transaction


@pytest.mark.asyncio
async def test_enqueue_transaction_admin_log_task_right_data(
    mocker: MockerFixture, save_fixture: SaveFixture, user: User
) -> None:
    enqueue_task_mock = mocker.patch("src.telegram_log.transaction.enqueue_task")

    ton_transaction = await create_ton_transaction(
        save_fixture, amount=5.01, message_hash="someMessageHash", hash="someTxHash"
    )
    transaction = await create_transaction(
        save_fixture,
        user,
        ton_transaction,
        amount=5.28,
        stars_amount=1337,
        recipient_username="dedushka",
    )

    enqueue_transaction_admin_log_task(transaction)

    fee_amount = transaction.amount - float(
        to_amount(transaction.ton_transaction.nano_amount)
    )

    text = ADMIN_TELEGRAM_TRANSACTION_TEXT.format(
        head_emoji=custom_emoji.TELEGRAM_STAR_ANIMATED.html,
        head_title_url=ADMIN_TELEGRAM_TRANSACTION_TITLE_TEMPLATE.format(
            hash=transaction.ton_transaction.hash
        )
        if transaction.ton_transaction.hash
        else "transaction",
        user_field=user.html_telegram_link,
        amount=5.28,
        fee_amount=fee_amount,
        username="@dedushka",
        value_str="1337 stars",
    )
    enqueue_task_mock.assert_called_once_with(
        admin_telegram_notification_send,
        text=text,
        with_notification=transaction.amount > settings.MIN_NON_SILENT_AMOUNT,
    )


async def _bulk(
    save_fixture: SaveFixture, user: User, count: int, *, amount: float = 1.5
) -> list[Transaction]:
    return [
        await create_transaction(
            save_fixture,
            user,
            await create_ton_transaction(save_fixture, amount=1),
            amount=amount,
            stars_amount=1000 + i,
            recipient_username=f"user{i}",
        )
        for i in range(count)
    ]


@pytest.mark.asyncio
async def test_enqueue_bulk_admin_log_is_one_digest(
    mocker: MockerFixture, save_fixture: SaveFixture, user: User
) -> None:
    enqueue_task_mock = mocker.patch("src.telegram_log.transaction.enqueue_task")
    transactions = await _bulk(save_fixture, user, 3)

    enqueue_bulk_transaction_admin_log_tasks(transactions)

    text = ADMIN_TELEGRAM_BULK_TRANSACTION_TEXT.format(
        head_emoji=custom_emoji.TELEGRAM_STAR_ANIMATED.html,
        head_title_url="transaction",
        count=3,
        user_field=user.html_telegram_link,
        amount=4.5,
        fee_amount=1.5,
        total_field="Total: <b>3 003 stars</b>\n",
        recipients=(
            "1. @user0 — 1 000 stars\n"
            "2. @user1 — 1 001 stars\n"
            "3. @user2 — 1 002 stars"
        ),
    )
    assert "<blockquote>1. @user0 — 1 000 stars\n" in text
    enqueue_task_mock.assert_called_once_with(
        admin_telegram_notification_send,
        text=text,
        with_notification=4.5 > settings.MIN_NON_SILENT_AMOUNT,
    )


@pytest.mark.asyncio
async def test_enqueue_bulk_admin_log_notifies_on_batch_total(
    mocker: MockerFixture, save_fixture: SaveFixture, user: User
) -> None:
    enqueue_task_mock = mocker.patch("src.telegram_log.transaction.enqueue_task")
    # Each purchase is below the threshold, the batch is above it.
    amount = settings.MIN_NON_SILENT_AMOUNT * 0.75
    transactions = await _bulk(save_fixture, user, 2, amount=amount)

    enqueue_bulk_transaction_admin_log_tasks(transactions)

    assert enqueue_task_mock.call_args.kwargs["with_notification"] is True


@pytest.mark.asyncio
async def test_enqueue_bulk_admin_log_splits_long_recipient_list(
    mocker: MockerFixture, save_fixture: SaveFixture, user: User
) -> None:
    enqueue_task_mock = mocker.patch("src.telegram_log.transaction.enqueue_task")
    transactions = await _bulk(save_fixture, user, BULK_LINES_PER_MESSAGE + 2)

    enqueue_bulk_transaction_admin_log_tasks(transactions)

    assert enqueue_task_mock.call_count == 2
    first, second = (call.kwargs for call in enqueue_task_mock.call_args_list)
    assert f"{BULK_LINES_PER_MESSAGE}. @user{BULK_LINES_PER_MESSAGE - 1} " in (
        first["text"]
    )
    assert f"{BULK_LINES_PER_MESSAGE + 1}. " not in first["text"]
    last = BULK_LINES_PER_MESSAGE + 1
    assert second["text"] == ADMIN_TELEGRAM_BULK_TRANSACTION_NEXT_TEXT.format(
        head_emoji=custom_emoji.TELEGRAM_STAR_ANIMATED.html,
        part=2,
        parts=2,
        recipients=(
            f"{last}. @user{last - 1} — {1000 + last - 1:,} stars\n"
            f"{last + 1}. @user{last} — {1000 + last:,} stars"
        ).replace(",", " "),
    )
    # Only the first part may ping.
    assert second["with_notification"] is False
    assert all(len(call["text"]) < 4096 for call in (first, second))


@pytest.mark.asyncio
async def test_enqueue_bulk_user_log_is_one_digest(
    mocker: MockerFixture, save_fixture: SaveFixture, user: User
) -> None:
    enqueue_task_mock = mocker.patch("src.telegram_log.transaction.enqueue_task")
    transactions = await _bulk(save_fixture, user, 2)

    enqueue_bulk_transaction_telegram_log_tasks(
        source=MagicMock(chat_id="-100123"), transactions=transactions
    )

    enqueue_task_mock.assert_called_once_with(
        telegram_log_send,
        chat_id="-100123",
        text=USER_TELEGRAM_BULK_LOG_TEXT.format(
            head_emoji=custom_emoji.TELEGRAM_STAR_ANIMATED.html,
            reason=transactions[0].reason,
            count=2,
            amount=3.0,
            total_field="Всего: <b>2 001 звезд</b>\n",
            recipients="1. @user0 — 1 000 звезд\n2. @user1 — 1 001 звезд",
        ),
        with_notification=True,
    )
