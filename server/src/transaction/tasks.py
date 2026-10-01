import uuid
from datetime import timedelta
from typing import Annotated

import structlog
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from taskiq import TaskiqDepends
from ton_core import Address, ExternalMessage, WalletV5Params
from tonutils.contracts.wallet.messages import TONTransferBuilder

from src.exceptions import BadRequest, ResourceNotFound
from src.fee import approx_before_fee
from src.kit.ton_connect import TonConnectTransaction
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import Deposit, Transaction, User
from src.models.deposits import DepositStatus
from src.postgres import AsyncSession
from src.telegram_log.service import telegram_log as telegram_log_service
from src.telegram_log.tasks import admin_telegram_notification_send
from src.telegram_log.transaction import (
    enqueue_transaction_admin_log_task,
    enqueue_transaction_telegram_log_task,
)
from src.ton_transaction.tasks import ton_transaction_find_real_hash
from src.transaction.repository import TransactionRepository
from src.transaction.utils import validate_tc_transaction
from src.wallet.manager import WalletManager
from src.wallet.send_gate import WalletSendGate
from src.worker import enqueue_task, worker_task_with_queue_manager
from src.worker.sqlalchemy import get_async_session
from src.worker.wallet_manager import get_wallet_manager
from src.worker.wallet_send_gate import get_wallet_send_gate

log: Logger = structlog.get_logger()


@worker_task_with_queue_manager(task_name="transaction.process")
async def fragment_transaction_process(
    transaction_id: uuid.UUID,
    tc_transaction: TonConnectTransaction,
    session: Annotated[AsyncSession, TaskiqDepends(get_async_session)],
    wallet_manager: Annotated[WalletManager, TaskiqDepends(get_wallet_manager)],
    send_gate: Annotated[WalletSendGate, TaskiqDepends(get_wallet_send_gate)],
) -> None:
    validate_tc_transaction(tc_transaction=tc_transaction)

    repository = TransactionRepository.from_session(session)
    transaction = await repository.get_by_id(
        id=transaction_id,
        options=[
            selectinload(Transaction.user),
            selectinload(Transaction.ton_transaction),
        ],
    )

    if transaction is None:
        log.warning(
            "transaction.process.not_found",
            transaction_id=transaction_id,
        )
        raise ResourceNotFound()

    log.debug(
        "transaction.process.start",
        user=transaction.user,
        amount=transaction.amount,
        recipient_username=transaction.recipient_username,
        stars_amount=transaction.stars_amount,
        premium_months=transaction.premium_months,
    )

    tc_msg = tc_transaction.messages[0]
    built_ext_msg = ExternalMessage(
        dest=Address(tc_msg.address), body=tc_msg.get_payload_cell()
    )

    if transaction.ton_transaction.message_hash != built_ext_msg.normalized_hash:
        log.warning(
            "transaction.process different transaction message hash and ext_msg hash"
        )
        raise BadRequest("Hash is bad")

    body = tc_msg.get_payload_cell()
    valid_until = int(tc_transaction.valid_until.timestamp()) + 10

    async with send_gate.attempt():
        # Reload after waiting: another delivery of this same job may have sent it.
        await session.refresh(
            transaction,
            attribute_names=["outgoing_message_hash"],
        )
        if transaction.outgoing_message_hash:
            log.info("transaction.process.skip_already_submitted")
            enqueue_task(
                ton_transaction_find_real_hash,
                ton_transaction_id=transaction.ton_transaction_id,
            )
            return

        broadcast_started = False
        try:
            if utc_now().timestamp() >= valid_until:
                raise BadRequest("Queued transaction has expired")

            # Refresh/select/build inside the gate; doing this before waiting
            # could sign multiple sends with the same stale wallet seqno.
            wallet = await wallet_manager.get_wallet_for_amount(amount=tc_msg.amount)
            ext_msg = await wallet.build_external_message(
                [
                    TONTransferBuilder(
                        destination=Address(tc_msg.address),
                        body=body,
                        amount=tc_msg.amount,
                    )
                ],
                params=WalletV5Params(valid_until=valid_until),
            )
            transaction.outgoing_message_hash = ext_msg.normalized_hash
            # Commit the exact outgoing identifier BEFORE any network submission.
            await session.commit()
            broadcast_started = True
            await wallet.client.send_message(ext_msg.as_hex)
            transaction.ton_transaction.hash = ext_msg.normalized_hash
            transaction.sent_at = utc_now()
            await session.commit()
        except BaseException as exc:
            await session.commit()
            log.exception("transaction.process.send_failed")
            if not isinstance(exc, Exception):
                raise
            # Ambiguous sends are reconciled, never blindly broadcast again.
            if broadcast_started:
                enqueue_task(
                    ton_transaction_find_real_hash,
                    ton_transaction_id=transaction.ton_transaction_id,
                )
            return

    log.info(
        "transaction.process.transfered",
        destination=tc_msg.address,
        amount=tc_msg.amount,
        normalized_hash=ext_msg.normalized_hash,
    )

    try:
        enqueue_transaction_admin_log_task(transaction=transaction)
    except Exception:
        log.exception("transaction.process.error_enqueuing_admin_log")

    try:
        sources = await telegram_log_service.get_all_sources(
            session=session, user=transaction.user
        )
        sources_count = len(sources)

        if sources_count == 1:  # PERF: dont forget to change it to > 1 or smth
            enqueue_transaction_telegram_log_task(
                source=sources[0], transaction=transaction
            )
        elif sources_count > 1:
            log.warning(
                "transaction.process.skip_enqueue_user_log somehow sources number is bigger than 1",
                sources_count=sources_count,
            )
    except Exception:
        log.exception("transaction.process.error_enqueuing_user_log")

    enqueue_task(
        ton_transaction_find_real_hash,
        ton_transaction_id=transaction.ton_transaction_id,
    )


DAILY_LOG_TEXT = (
    "🗓 Daily stats - {date} \n\n"
    "Total balance: <b>{total_balance:.2f} GRAM</b>\n\n"
    "Volume: <b>{volume:.2f} GRAM</b>\n"
    "Raw commission amount: <b>{raw_commission_amount:.2f} GRAM</b>\n\n"
    "Transactions: <b>{transactions_count}</b> 🧾\n"
    "Transactions unique users: <b>{transactions_unique_users}</b> 👤\n\n"
    "Users: <b>{new_users_count}</b> 🐣 [<i>{users_total_count}</i>]\n"
    "Deposits: [<i>Req{deposit_requests_count}</i>] <b>{deposits_count}</b> - <b>{deposits_amount:.2f} GRAM</b> 📊"
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
    users_total_count = await session.scalar(select(func.count(User.id))) or 0

    deposit_stmt = select(
        func.count(Deposit.id), func.coalesce(func.sum(Deposit.amount), 0)
    ).where(
        func.date(Deposit.created_at) == yesterday_date,
        Deposit.status == DepositStatus.completed,
    )
    dep_result = await session.execute(deposit_stmt)
    deposits_count, deposits_amount = dep_result.one()

    dep_req_stmt = select(func.count(Deposit.id)).where(
        func.date(Deposit.created_at) == yesterday_date
    )
    deposit_requests_count = await session.scalar(dep_req_stmt) or 0

    enqueue_task(
        admin_telegram_notification_send,
        text=DAILY_LOG_TEXT.format(
            date=yesterday_date.strftime("%m-%d"),
            total_balance=total_balance,
            volume=volume_amount,
            raw_commission_amount=approx_before_fee(volume_amount),
            transactions_count=should_be_count,
            transactions_unique_users=transactions_unique_users,
            new_users_count=new_users,
            deposits_count=deposits_count,
            deposits_amount=deposits_amount,
            users_total_count=users_total_count,
            deposit_requests_count=deposit_requests_count,
        ),
        with_notification=False,
    )
