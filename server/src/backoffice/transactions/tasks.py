from datetime import timedelta
from typing import Annotated

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from src.backoffice.telegram_logs.tasks import telegram_log_send
from src.fee import approx_before_fee
from src.kit.utils import utc_now
from src.models import Deposit, Transaction, User
from src.models.deposits import DepositStatus
from src.worker import enqueue_task, worker_task_with_queue_manager
from src.worker.sqlalchemy import get_async_session

DAILY_LOG_TEXT = (
    "🗓 Daily stats - {date} \n\n"
    "Total balance: <b>{total_balance:.2f} GRAM</b>\n\n"
    "Volume: <b>{volume:.2f} GRAM</b>\n"
    "Raw commission amount: <b>{raw_commission_amount:.2f} GRAM</b>\n\n"
    "Transactions: <b>{transactions_count}</b> 🧾\n"
    "Transactions unique users: <b>{transactions_unique_users}</b> 👤\n\n"
    "New users: <b>{new_users_count}</b> 🐣\n"
    "Deposits: <b>{deposits_count}</b> - <b>{deposits_amount:.2f} GRAM</b> 📊"
)


@worker_task_with_queue_manager(
    task_name="admin_transactions.log_daily_stats",
    schedule=[{"cron": "0 0 * * *"}],
)
async def transactions_log_daily_stats(
    session: Annotated[AsyncSession, TaskiqDepends(get_async_session)],
) -> None:
    yesterday_date = (utc_now() - timedelta(days=1)).date()

    total_balance = await session.scalar(select(func.sum(User.balance))) or 0

    trans_stmt = select(
        func.coalesce(func.sum(Transaction.amount), 0),
        func.count(Transaction.id),
        func.count(func.distinct(Transaction.user_id)),
    ).where(func.date(Transaction.created_at) == yesterday_date)

    t_row = await session.execute(trans_stmt)
    volume_amount, should_be_count, transactions_unique_users = t_row.one()

    new_users = (
        await session.scalar(
            select(func.count(User.id)).where(
                func.date(User.created_at) == yesterday_date
            )
        )
        or 0
    )

    deposits_stmt = select(
        func.count(Deposit.id), func.coalesce(func.sum(Deposit.amount), 0)
    ).where(
        func.date(Deposit.created_at) == yesterday_date,
        Deposit.status == DepositStatus.completed,
    )

    d_row = await session.execute(deposits_stmt)
    new_deposits_count, new_deposits_amount = d_row.one()

    enqueue_task(
        telegram_log_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_date.strftime("%m-%d"),
            total_balance=total_balance,
            volume=volume_amount,
            raw_commission_amount=approx_before_fee(volume_amount),
            transactions_count=should_be_count,
            transactions_unique_users=transactions_unique_users,
            new_users_count=new_users,
            deposits_count=new_deposits_count,
            deposits_amount=new_deposits_amount,
        ),
        with_notification=False,
    )
