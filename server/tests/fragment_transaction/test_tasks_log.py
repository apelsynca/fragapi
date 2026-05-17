from unittest.mock import ANY, MagicMock

import pytest
from pytest_mock import MockerFixture

from src.bot.logs_sender import TelegramLogSender
from src.config import settings
from src.fragment_transaction.tasks import send_telegram_log
from src.models import Transaction, User
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_fragment_transaction


@pytest.fixture
def telegram_log_sender(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.fragment_transaction.tasks.telegram_log_sender", spec=TelegramLogSender
    )


@pytest.mark.asyncio
async def test_sends_with_notification_if_more_than_cfgval_ton(
    save_fixture: SaveFixture,
    user: User,
    transaction: Transaction,
    telegram_log_sender: MagicMock,
) -> None:
    frag_transaction = await create_fragment_transaction(
        save_fixture,
        user=user,
        transaction=transaction,
        amount=settings.MIN_NON_SILENT_AMOUNT + 0.1,
    )

    await send_telegram_log(fragment_transaction_id=frag_transaction.id)

    telegram_log_sender.send.assert_called_once_with(text=ANY, with_notification=True)


@pytest.mark.asyncio
async def test_sends_without_notification_if_less_than_cfgval_ton(
    save_fixture: SaveFixture,
    user: User,
    transaction: Transaction,
    telegram_log_sender: MagicMock,
) -> None:
    frag_transaction = await create_fragment_transaction(
        save_fixture,
        user=user,
        transaction=transaction,
        amount=settings.MIN_NON_SILENT_AMOUNT - 0.1,
    )

    await send_telegram_log(fragment_transaction_id=frag_transaction.id)

    telegram_log_sender.send.assert_called_once_with(text=ANY, with_notification=False)
