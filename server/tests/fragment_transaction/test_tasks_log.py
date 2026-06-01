from unittest.mock import ANY, MagicMock

import pytest

from src.config import settings
from src.fragment_transaction.tasks import send_telegram_log
from src.models import Transaction, User
from src.postgres import AsyncSession
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_fragment_transaction


@pytest.mark.asyncio
async def test_sends_with_notification_if_more_than_cfgval_ton(
    save_fixture: SaveFixture,
    user: User,
    transaction: Transaction,
    telegram_log_sender: MagicMock,
    session: AsyncSession,
) -> None:
    frag_transaction = await create_fragment_transaction(
        save_fixture,
        user=user,
        transaction=transaction,
        amount=settings.MIN_NON_SILENT_AMOUNT + 0.1,
    )

    await send_telegram_log(
        fragment_transaction_id=frag_transaction.id, session=session
    )

    telegram_log_sender.send.assert_called_once_with(text=ANY, with_notification=True)


@pytest.mark.asyncio
async def test_sends_without_notification_if_less_than_cfgval_ton(
    save_fixture: SaveFixture,
    user: User,
    transaction: Transaction,
    telegram_log_sender: MagicMock,
    session: AsyncSession,
) -> None:
    frag_transaction = await create_fragment_transaction(
        save_fixture,
        user=user,
        transaction=transaction,
        amount=settings.MIN_NON_SILENT_AMOUNT - 0.1,
    )

    await send_telegram_log(
        fragment_transaction_id=frag_transaction.id, session=session
    )

    telegram_log_sender.send.assert_called_once_with(text=ANY, with_notification=False)
