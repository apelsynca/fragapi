from datetime import timedelta
from typing import Annotated

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from src.backoffice.telegram_logs.tasks import telegram_log_send
from src.kit.utils import utc_now
from src.models import FragmentTransaction
from src.worker import enqueue_task, worker_task_with_queue_manager
from src.worker.sqlalchemy import get_async_session

DAILY_LOG_TEXT = (
    "🗓 Daily stats - {date} \n\n"
    "Amount: <b>{amount:.2f} GRAM</b>\n"
    "Transactions: <b>{transactions_count}</b>\n"
    "Unique users: <b>{unique_users}</b>"
)


@worker_task_with_queue_manager(
    task_name="admin_fragment_transactions.log_daily_stats",
    schedule=[{"cron": "0 0 * * *"}],
)
async def fragment_transactions_log_daily_stats(
    session: Annotated[AsyncSession, TaskiqDepends(get_async_session)],
) -> None:
    yesterday_date = (utc_now() - timedelta(days=1)).date()
    stmt = select(
        func.coalesce(func.sum(FragmentTransaction.amount), 0),
        func.count(FragmentTransaction.id),
        func.count(func.distinct(FragmentTransaction.amount)),
    ).where(func.date(FragmentTransaction.created_at) == yesterday_date)

    row = await session.execute(stmt)
    total_amount, should_be_count, unique_users = row.one()

    enqueue_task(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_date.strftime("%m-%d"),
            amount=total_amount,
            transactions_count=should_be_count,
            unique_users=unique_users,
        ),
        with_notification=False,
    )
