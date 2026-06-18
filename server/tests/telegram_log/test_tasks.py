from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.telegram_log.sender import BaseTelegramLogSender, TelegramLogChatNotFound
from src.telegram_log.tasks import telegram_log_send


@pytest.fixture
def telegram_log_sender_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.telegram_log.tasks.telegram_log_sender", spec=BaseTelegramLogSender
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("with_notification", [True, False])
async def test_telegram_log_send_calls_log_sender_right_data(
    telegram_log_sender_mock: MagicMock, with_notification: bool
) -> None:
    await telegram_log_send(
        chat_id=1337, text="SomeText", with_notification=with_notification
    )

    telegram_log_sender_mock.send.assert_called_once_with(
        chat_id=1337, text="SomeText", with_notification=with_notification
    )


@pytest.mark.asyncio
async def test_telegram_log_send_not_found_do_not_raise(
    telegram_log_sender_mock: MagicMock,
) -> None:
    telegram_log_sender_mock.send.side_effect = TelegramLogChatNotFound()

    await telegram_log_send(chat_id=9195, text="Other text", with_notification=False)

    telegram_log_sender_mock.send.assert_called_once_with(
        chat_id=9195, text="Other text", with_notification=False
    )


@pytest.mark.asyncio
async def test_telegram_log_reraises_if_unknown_exc(
    telegram_log_sender_mock: MagicMock,
) -> None:
    telegram_log_sender_mock.send.side_effect = Exception("Unknown exception")

    with pytest.raises(Exception, match="Unknown exception"):
        await telegram_log_send(chat_id=9129, text="Valid text", with_notification=True)

    telegram_log_sender_mock.send.assert_called_once_with(
        chat_id=9129, text="Valid text", with_notification=True
    )
