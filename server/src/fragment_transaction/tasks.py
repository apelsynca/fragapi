import uuid
from typing import Annotated

import structlog
from sqlalchemy.orm import selectinload
from taskiq import TaskiqDepends
from ton_core import Address, ExternalMessage, WalletV5Params

from src.backoffice.telegram_logs.fragment_transactions import (
    enqueue_frag_trans_admin_log_task,
)
from src.exceptions import BadRequest, ResourceNotFound
from src.fragment_transaction.repository import FragmentTransactionRepository
from src.fragment_transaction.utils import validate_tc_transaction
from src.integrations.ton_wallet.manager import WalletManager
from src.kit.ton_connect import TonConnectTransaction
from src.logging import Logger
from src.models import FragmentTransaction
from src.postgres import AsyncSession
from src.telegram_log.fragment_transaction import enqueue_new_trans_telegram_log_task
from src.telegram_log.service import telegram_log as telegram_log_service
from src.worker import worker_task_with_queue_manager
from src.worker.sqlalchemy import get_async_session
from src.worker.wallet_manager import get_wallet_manager

log: Logger = structlog.get_logger()


@worker_task_with_queue_manager()
async def process_fragment_transaction(
    fragment_transaction_id: uuid.UUID,
    tc_transaction: TonConnectTransaction,
    session: Annotated[AsyncSession, TaskiqDepends(get_async_session)],
    wallet_manager: Annotated[WalletManager, TaskiqDepends(get_wallet_manager)],
) -> None:
    validate_tc_transaction(tc_transaction=tc_transaction)

    repository = FragmentTransactionRepository.from_session(session)
    fragment_transaction = await repository.get_by_id(
        id=fragment_transaction_id,
        options=[
            selectinload(FragmentTransaction.user),
            selectinload(FragmentTransaction.transaction),
        ],
    )

    if fragment_transaction is None:
        log.warning(
            "process_fragment_transaction.not_found",
            fragment_transaction_id=fragment_transaction_id,
        )
        raise ResourceNotFound()

    log.debug(
        "process_fragment_transaction.start",
        user=fragment_transaction.user,
        amount=fragment_transaction.amount,
        recipient_username=fragment_transaction.recipient_username,
        stars_amount=fragment_transaction.stars_amount,
        premium_months=fragment_transaction.premium_months,
    )

    tc_msg = tc_transaction.messages[0]
    built_ext_msg = ExternalMessage(
        dest=Address(tc_msg.address), body=tc_msg.get_payload_cell()
    )

    if fragment_transaction.transaction.message_hash != built_ext_msg.normalized_hash:
        log.warning(
            "process_fragment_transaction Different transaction message hash and ext_msg hash"
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

    fragment_transaction.transaction.hash = ext_msg.normalized_hash

    try:
        enqueue_frag_trans_admin_log_task(fragment_transaction)
    except Exception:
        log.error("Error enqueuing fragment transaction admin log", exc_info=True)

    try:
        sources = await telegram_log_service.get_all_sources(
            session=session, user=fragment_transaction.user
        )
        if len(sources) == 1:  # PERF: dont forget to change it to > 1 or smth
            enqueue_new_trans_telegram_log_task(sources[0], fragment_transaction)
    except Exception:
        log.error("Error enqueuing fragment transaction admin log", exc_info=True)
