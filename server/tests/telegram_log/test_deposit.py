import pytest
from pytest_mock import MockerFixture

from src.models import Deposit, User
from src.telegram_log.deposit import (
    NEW_DEPOSIT_NOTIFICATION_TEXT,
    NEW_DEPOSIT_TON_TRANSACTION_TEXT,
    enqueue_new_deposit_admin_log_task,
)
from src.telegram_log.tasks import admin_telegram_log_send
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction


@pytest.mark.asyncio
async def test_enqueue_new_deposit_right_calls(
    save_fixture: SaveFixture, user: User, mocker: MockerFixture
) -> None:
    user.balance = 10

    enqueue_task_mock = mocker.patch("src.telegram_log.deposit.enqueue_task")

    deposit = Deposit(user=user, amount=5.1259, hash="MyHash1i-ek91_25")
    await save_fixture(deposit)
    enqueue_new_deposit_admin_log_task(deposit=deposit)

    expected_user_field = (
        f"<a href='tg://resolve?domain={user.username}'>{user.first_name}</a>"
        if user.username
        else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    )
    enqueue_task_mock.assert_called_once_with(
        admin_telegram_log_send,
        text=NEW_DEPOSIT_NOTIFICATION_TEXT.format(
            amount=5.1259,
            user_field=expected_user_field,
            ref_hash="MyHash1i-ek91_25",
            ton_transaction_field="",
            prev_balance=10 - 5.1259,
            curr_balance=10,
        ),
        with_notification=True,
    )


@pytest.mark.asyncio
async def test_enqueue_new_deposit_with_ton_transaction_right_calls(
    save_fixture: SaveFixture, user: User, mocker: MockerFixture
) -> None:
    user.balance = 250

    enqueue_task_mock = mocker.patch("src.telegram_log.deposit.enqueue_task")

    ton_transaction = await create_ton_transaction(
        save_fixture,
        amount=300,
        message_hash=None,
        hash="someTransaction0x0x0x0Hash5-125_asd9as2",
    )
    deposit = Deposit(
        user=user, amount=300, hash="DiffieHash", ton_transaction=ton_transaction
    )
    await save_fixture(deposit)
    enqueue_new_deposit_admin_log_task(deposit=deposit)

    expected_user_field = (
        f"<a href='tg://resolve?domain={user.username}'>{user.first_name}</a>"
        if user.username
        else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    )
    ton_trans_text = NEW_DEPOSIT_TON_TRANSACTION_TEXT.format(
        "someTransaction0x0x0x0Hash5-125_asd9as2"
    )
    assert (
        "https://tonscan.org/tx/someTransaction0x0x0x0Hash5-125_asd9as2"
        in ton_trans_text
    )
    enqueue_task_mock.assert_called_once_with(
        admin_telegram_log_send,
        text=NEW_DEPOSIT_NOTIFICATION_TEXT.format(
            amount=300,
            user_field=expected_user_field,
            ref_hash="DiffieHash",
            ton_transaction_field=ton_trans_text,
            prev_balance=-50,  # yeah, fine for now
            curr_balance=250,
        ),
        with_notification=True,
    )
