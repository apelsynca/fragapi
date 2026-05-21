import uuid

import pytest
from pytest_mock import MockerFixture

from src.bot.logs_sender import TelegramLogSender
from src.exceptions import ResourceNotFound
from src.models.payments import Payment
from src.payment.tasks import NEW_DEPOSIT_NOTIFICATION_TEXT, deposit_send_telegram_log


@pytest.mark.asyncio
async def test_telegram_log_raises_if_not_found() -> None:
    with pytest.raises(ResourceNotFound):
        await deposit_send_telegram_log(payment_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_telegram_log_right_message_and_notify(
    payment: Payment, mocker: MockerFixture
) -> None:
    user_field = (
        f"<a href='tg://resolve?domain={payment.user.username}'>{payment.user.first_name}</a>"
        if payment.user.username
        else f"<a href='tg://user?id={payment.user_id}'>{payment.user.first_name}</a>"
    )

    telegram_log_sender_mock = mocker.patch(
        "src.payment.tasks.telegram_log_sender", spec=TelegramLogSender
    )

    await deposit_send_telegram_log(payment_id=payment.id)
    telegram_log_sender_mock.send.assert_called_once_with(
        text=NEW_DEPOSIT_NOTIFICATION_TEXT.format(
            amount=payment.amount, user_field=user_field, hash=payment.hash
        ),
        with_notification=True,
    )
