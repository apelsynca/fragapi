from datetime import timedelta

import pytest

from src.deposit.tasks import deposit_set_failed_to_expired_ones
from src.kit.utils import utc_now
from src.models import Deposit
from src.models.deposits import DepositStatus
from src.models.users import User
from src.postgres import AsyncSession
from tests.fixtures.database import SaveFixture


@pytest.mark.asyncio
async def test_set_failed_to_old_pending_deposits(
    save_fixture: SaveFixture, session: AsyncSession, user: User, user_second: User
) -> None:
    now = utc_now()

    deposit_pending_new = Deposit(
        user=user,
        amount=1.25,
        hash="pendingNewDepHash",
        status=DepositStatus.pending,
        created_at=now,
    )
    deposit_pending_new_2 = Deposit(
        user=user_second,
        amount=3,
        hash="pendingNewOtherHash",
        status=DepositStatus.pending,
        created_at=now,
    )
    deposit_pending_old = Deposit(
        user=user,
        amount=51.25,
        hash="somePendingHash",
        status=DepositStatus.pending,
        created_at=now - timedelta(hours=1.1),
    )
    deposit_completed_old = Deposit(
        user=user,
        amount=510,
        hash="diffieHash",
        status=DepositStatus.completed,
        created_at=now - timedelta(hours=1.1),
    )
    await save_fixture(deposit_pending_new)
    await save_fixture(deposit_pending_new_2)
    await save_fixture(deposit_pending_old)
    await save_fixture(deposit_completed_old)

    await deposit_set_failed_to_expired_ones(session=session)

    assert deposit_pending_new.status == DepositStatus.pending
    assert deposit_pending_new_2.status == DepositStatus.pending
    assert deposit_pending_old.status == DepositStatus.failed
    assert deposit_completed_old.status == DepositStatus.completed
