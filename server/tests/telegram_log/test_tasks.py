# from unittest.mock import MagicMock
#
# import pytest
# from pytest_mock import MockerFixture
#
# from src.telegram_log.tasks import telegram_log_send
#
#
# @pytest.fixture
# def telegram_log_sender_mock(mocker: MockerFixture) -> MagicMock:
#     return mocker.patch("src.telegram_log.tasks.telegram_log_sender")
#
#
# @pytest.mark.asyncio
# async def test_telegram_log_send_calls_log_sender(
#     telegram_log_sender_mock: MagicMock,
# ) -> None:
#     await telegram_log_send(text="Hello world", with_notification=False)
#
#     telegram_log_sender_mock.assert_called_once_with()
#
#
# @pytest.mark.asyncio
# async def test_telegram_log_send_error_logs(
#     telegram_log_sender_mock: MagicMock,
# ) -> None:
#     await telegram_log_send(text="Hello world", with_notification=False)
#
#     telegram_log_sender_mock.assert_called_once()
