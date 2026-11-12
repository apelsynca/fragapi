from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import AiogramError, TelegramRetryAfter
from pytest_mock import MockerFixture

from src.telegram_log.sender import BaseTelegramLogSender, TelegramLogChatNotFound
from src.telegram_log.tasks import (
    MAX_FLOOD_RETRIES,
    admin_telegram_log_send,
    admin_telegram_notification_send,
    telegram_log_send,
)


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


@pytest.fixture
def admin_telegram_notification_sender_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.telegram_log.tasks.admin_telegram_notification_sender",
        spec=BaseTelegramLogSender,
    )


@pytest.fixture
def admin_telegram_log_sender_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.telegram_log.tasks.admin_telegram_log_sender",
        spec=BaseTelegramLogSender,
    )


@pytest.mark.asyncio
async def test_telegram_notification_send_calls_log_sender(
    admin_telegram_notification_sender_mock: MagicMock,
) -> None:
    await admin_telegram_notification_send(text="Hello world", with_notification=False)

    admin_telegram_notification_sender_mock.send.assert_called_once_with(
        text="Hello world", with_notification=False
    )


@pytest.mark.asyncio
async def test_telegram_notification_send_error_logs(
    admin_telegram_notification_sender_mock: MagicMock, mocker: MockerFixture
) -> None:
    log_mock = mocker.patch("src.telegram_log.tasks.log")

    admin_telegram_notification_sender_mock.send.side_effect = AiogramError()

    with pytest.raises(AiogramError):
        await admin_telegram_notification_send(
            text="Hello world", with_notification=False
        )

    admin_telegram_notification_sender_mock.send.assert_called_once()
    log_mock.exception.assert_called_once()


@pytest.mark.asyncio
async def test_telegram_log_send_calls_log_sender(
    admin_telegram_log_sender_mock: MagicMock,
) -> None:
    await admin_telegram_log_send(text="Hello world", with_notification=False)

    admin_telegram_log_sender_mock.send.assert_called_once_with(
        text="Hello world", with_notification=False
    )


@pytest.mark.asyncio
async def test_telegram_log_send_error_logs(
    admin_telegram_log_sender_mock: MagicMock, mocker: MockerFixture
) -> None:
    log_mock = mocker.patch("src.telegram_log.tasks.log")

    admin_telegram_log_sender_mock.send.side_effect = AiogramError()

    with pytest.raises(AiogramError):
        await admin_telegram_log_send(text="Hello world", with_notification=False)

    admin_telegram_log_sender_mock.send.assert_called_once()
    log_mock.exception.assert_called_once()


def _flood(retry_after: int = 7) -> TelegramRetryAfter:
    return TelegramRetryAfter(
        method=MagicMock(), message="Too Many Requests", retry_after=retry_after
    )


@pytest.mark.asyncio
async def test_admin_notification_flood_is_rescheduled_after_retry_after(
    admin_telegram_notification_sender_mock: MagicMock, mocker: MockerFixture
) -> None:
    admin_telegram_notification_sender_mock.send.side_effect = _flood(7)
    kicker_mock = mocker.patch.object(admin_telegram_notification_send, "kicker")
    kiq_mock = kicker_mock.return_value.with_labels.return_value.kiq = AsyncMock()

    await admin_telegram_notification_send(text="Hello", with_notification=True)

    delay = kicker_mock.return_value.with_labels.call_args.kwargs["delay"]
    assert 7 < delay <= 12
    kiq_mock.assert_awaited_once_with(text="Hello", with_notification=True, attempt=1)


@pytest.mark.asyncio
async def test_user_log_flood_is_rescheduled_with_same_message(
    telegram_log_sender_mock: MagicMock, mocker: MockerFixture
) -> None:
    telegram_log_sender_mock.send.side_effect = _flood()
    kicker_mock = mocker.patch.object(telegram_log_send, "kicker")
    kiq_mock = kicker_mock.return_value.with_labels.return_value.kiq = AsyncMock()

    await telegram_log_send(chat_id=1, text="Hi", with_notification=False, attempt=2)

    kiq_mock.assert_awaited_once_with(
        chat_id=1, text="Hi", with_notification=False, attempt=3
    )


@pytest.mark.asyncio
async def test_flood_gives_up_after_max_retries(
    admin_telegram_log_sender_mock: MagicMock, mocker: MockerFixture
) -> None:
    admin_telegram_log_sender_mock.send.side_effect = _flood()
    kicker_mock = mocker.patch.object(admin_telegram_log_send, "kicker")

    with pytest.raises(TelegramRetryAfter):
        await admin_telegram_log_send(
            text="Hello", with_notification=False, attempt=MAX_FLOOD_RETRIES
        )

    kicker_mock.assert_not_called()
