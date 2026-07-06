import uuid
from typing import Annotated

import structlog
from sqlalchemy.orm import selectinload
from taskiq import TaskiqDepends
from ton_core import Address, ExternalMessage, WalletV5Params

from src.backoffice.telegram_logs.transactions import enqueue_transaction_admin_log_task
from src.exceptions import BadRequest, ResourceNotFound
from src.kit.ton_connect import TonConnectTransaction
from src.logging import Logger
from src.models import Transaction
from src.postgres import AsyncSession
from src.telegram_log.service import telegram_log as telegram_log_service
from src.telegram_log.transaction import enqueue_transaction_telegram_log_task
from src.transaction.repository import TransactionRepository
from src.transaction.utils import validate_tc_transaction
from src.wallet.manager import WalletManager
from src.worker import worker_task_with_queue_manager
from src.worker.sqlalchemy import get_async_session
from src.worker.wallet_manager import get_wallet_manager

log: Logger = structlog.get_logger()


@worker_task_with_queue_manager(task_name="transaction.process")
async def fragment_transaction_process(
    transaction_id: uuid.UUID,
    tc_transaction: TonConnectTransaction,
    session: Annotated[AsyncSession, TaskiqDepends(get_async_session)],
    wallet_manager: Annotated[WalletManager, TaskiqDepends(get_wallet_manager)],
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

    wallet = await wallet_manager.get_wallet_for_amount(amount=tc_msg.amount)

    body = tc_msg.get_payload_cell()
    valid_until = int(tc_transaction.valid_until.timestamp()) + 10

    ext_msg = await wallet.transfer(
        destination=Address(tc_msg.address),
        body=body,
        amount=tc_msg.amount,
        params=WalletV5Params(valid_until=valid_until),
    )

    transaction.ton_transaction.hash = ext_msg.normalized_hash

    log.info(
        "transaction.process.transfered",
        destination=tc_msg.address,
        amount=tc_msg.amount,
        normalized_hash=ext_msg.normalized_hash,
    )

    try:
        enqueue_transaction_admin_log_task(transaction=transaction)
    except Exception:
        log.error(
            "transaction.process.error_enqueuing_admin_log",
            exc_info=True,
        )

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
        log.error(
            "transaction.process.error_enqueuing_user_log",
            exc_info=True,
        )
