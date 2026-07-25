# import pytest
# from pytest_mock import MockerFixture
#
# from src.models import Transaction
# from src.telegram_log.tasks import admin_telegram_log_send
# from src.telegram_log.transaction import ADMIN_TELEGRAM_LOG_TEXT, enqueue_transaction_admin_log_task
#
#
# @pytest.mark.asyncio
# async def test_enqueue_right_data(
#     transaction: Transaction, mocker: MockerFixture
# ) -> None:
#     enqueue_task_mock = mocker.patch("src.telegram_log.transaction.enqueue_task")
#
#     enqueue_transaction_admin_log_task(transaction)
#
#     text = ADMIN_TELEGRAM_LOG_TEXT.format(head_emoji="⭐️", )
#
#     enqueue_task_mock.assert_called_once_with(
#         admin_telegram_log_send, text=text, with_notification=False
#     )
