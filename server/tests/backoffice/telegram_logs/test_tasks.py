from unittest.mock import MagicMock

import pytest
from aiogram.exceptions import AiogramError
from pytest_mock import MockerFixture

from src.backoffice.telegram_logs.sender import BaseTelegramLogSender
from src.backoffice.telegram_logs.tasks import telegram_log_send


@pytest.fixture
def telegram_log_sender_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.backoffice.telegram_logs.tasks.telegram_log_sender",
        spec=BaseTelegramLogSender,
    )


@pytest.mark.asyncio
async def test_telegram_log_send_calls_log_sender(
    telegram_log_sender_mock: MagicMock,
) -> None:
    await telegram_log_send(text="Hello world", with_notification=False)

    telegram_log_sender_mock.send.assert_called_once_with(
        text="Hello world", with_notification=False
    )


@pytest.mark.asyncio
async def test_telegram_log_send_error_logs(
    telegram_log_sender_mock: MagicMock, mocker: MockerFixture
) -> None:
    log_mock = mocker.patch("src.backoffice.telegram_logs.tasks.log")

    telegram_log_sender_mock.send.side_effect = AiogramError()

    with pytest.raises(AiogramError):
        await telegram_log_send(text="Hello world", with_notification=False)

    telegram_log_sender_mock.send.assert_called_once()
    log_mock.error.assert_called_once()
