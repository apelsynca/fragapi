import asyncio
from typing import Annotated

import structlog
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends
from ton_core import Cell, Transaction, normalize_hash

from src.config import settings
from src.exceptions import BadRequest, ResourceNotFound
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import Transaction as PurchaseTransaction
from src.ton_transaction.repository import TonTransactionRepository
from src.wallet.ton import NETWORK, create_toncenter
from src.worker import broker
from src.worker.sqlalchemy import get_async_session

log: Logger = structlog.get_logger()


@broker.task(retry_on_error=True, max_retries=3)
async def ton_transaction_find_real_hash(
    ton_transaction_id: UUID4,
    session: Annotated[AsyncSession, TaskiqDepends(get_async_session)],
) -> None:
    await asyncio.sleep(3)

    repository = TonTransactionRepository.from_session(session=session)

    ton_transaction = await repository.get_by_id(id=ton_transaction_id)
    if ton_transaction is None:
        raise ResourceNotFound()

    purchase = await session.scalar(
        select(PurchaseTransaction).where(
            PurchaseTransaction.ton_transaction_id == ton_transaction_id
        )
    )
    expected_hash = (
        purchase.outgoing_message_hash if purchase else None
    ) or ton_transaction.hash
    if expected_hash is None:
        log.error("ton_transaction.find_real_hash")
        raise BadRequest("No hash for the transaction")

    since = ton_transaction.created_at.timestamp() - 60
    await session.commit()
    # Lookup tasks must not close the worker's shared sending HTTP client.
    toncenter_client = create_toncenter(NETWORK)
    async with toncenter_client:
        cursor: tuple[int, str] | None = None
        for _ in range(100):
            bc_trans_result = await toncenter_client.provider.get_transactions(
                address=settings.TON_ADDRESS,
                limit=100,
                lt=cursor[0] if cursor else None,
                from_hash=cursor[1] if cursor else None,
            )
            page = bc_trans_result.result or []
            oldest = None
            for bc_trans in page:
                if bc_trans.data is None:
                    continue
                cell = Cell.one_from_boc(bc_trans.data)
                bc_transaction = Transaction.deserialize(cell_slice=cell.begin_parse())
                if not isinstance(bc_transaction, Transaction):
                    raise TypeError("Expected a deserialized TON transaction")
                oldest = bc_transaction
                if (
                    bc_transaction.in_msg is None
                    or not bc_transaction.in_msg.is_external
                ):
                    continue
                ext_msg_hash = normalize_hash(bc_transaction.in_msg)
                if expected_hash != ext_msg_hash:
                    continue
                tx_hash = bc_transaction.cell.hash.hex()
                ton_transaction.hash = tx_hash
                if purchase:
                    purchase.sent_at = purchase.sent_at or utc_now()
                log.info(
                    "ton_transaction.find_real_hash.found",
                    new_hash=tx_hash,
                    ext_msg_hash=ext_msg_hash,
                    ton_transaction_id=ton_transaction_id,
                )
                return
            if oldest is None or oldest.now < since or len(page) < 100:
                break
            next_cursor = (oldest.lt, oldest.cell.hash.hex())
            if next_cursor == cursor:
                break
            cursor = next_cursor

    log.warning(
        "ton_transaction.find_real_hash.not_found_manual_handling_required",
        ton_transaction_id=ton_transaction_id,
    )
    raise RuntimeError("Outgoing message not indexed yet; reconcile without resending")
