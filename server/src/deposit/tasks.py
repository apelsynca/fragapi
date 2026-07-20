from datetime import timedelta

from sqlalchemy import update

from src.kit.utils import utc_now
from src.models import Deposit
from src.models.deposits import DepositStatus
from src.postgres import AsyncSession
from src.worker import broker


@broker.task(
    task_name="deposit.set_failed_to_expired_ones", schedule=[{"cron": "30 * * * *"}]
)
async def deposit_set_failed_to_expired_ones(session: AsyncSession) -> None:
    await session.execute(
        update(Deposit)
        .values(status=DepositStatus.failed)
        .where(
            Deposit.created_at < utc_now() - timedelta(hours=1),
            Deposit.status == DepositStatus.pending,
        )
    )
