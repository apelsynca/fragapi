from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.telegram_log.sender import BaseTelegramLogSender
from src.telegram_log.tasks import telegram_log_send


@pytest.fixture
def telegram_log_sender_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.telegram_log.tasks.telegram_log_sender", spec=BaseTelegramLogSender
    )


@pytest.mark.asyncio
async def test_telegram_log_send_calls_log_sender_right_data(
    telegram_log_sender_mock: MagicMock,
) -> None:
    await telegram_log_send(chat_id=1337, text="SomeText", with_notification=False)

    telegram_log_sender_mock.send.assert_called_once_with(
        chat_id=1337, text="SomeText", with_notification=False
    )
