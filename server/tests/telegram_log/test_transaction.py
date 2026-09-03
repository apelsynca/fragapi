import pytest
from pytest_mock import MockerFixture
from ton_core import to_amount

from src.config import settings
from src.models import User
from src.telegram_log.tasks import admin_telegram_notification_send
from src.telegram_log.transaction import (
    ADMIN_TELEGRAM_TRANSACTION_TEXT,
    ADMIN_TELEGRAM_TRANSACTION_TITLE_TEMPLATE,
    STAR_EMOJI,
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
        head_emoji=STAR_EMOJI,
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
