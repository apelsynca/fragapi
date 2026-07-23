import asyncio
from typing import Annotated

import structlog
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends
from ton_core import Cell, Transaction, normalize_hash

from src.config import settings
from src.exceptions import BadRequest, ResourceNotFound
from src.logging import Logger
from src.ton_transaction.repository import TonTransactionRepository
from src.wallet.ton import toncenter as toncenter_client
from src.worker import broker
from src.worker.sqlalchemy import get_async_session

log: Logger = structlog.get_logger()


@broker.task()
async def ton_transaction_find_real_hash(
    ton_transaction_id: UUID4,
    session: Annotated[AsyncSession, TaskiqDepends(get_async_session)],
) -> None:
    await asyncio.sleep(3)

    repository = TonTransactionRepository.from_session(session=session)

    ton_transaction = await repository.get_by_id(id=ton_transaction_id)
    if ton_transaction is None:
        raise ResourceNotFound()

    if ton_transaction.hash is None:
        log.error("ton_transaction.find_real_hash")
        raise BadRequest("No hash for the transaction")

    async with toncenter_client:
        bc_trans_result = await toncenter_client.provider.get_transactions(
            address=settings.TON_ADDRESS, limit=10
        )
        if bc_trans_result.result is None:
            log.warning("No transactions found.")
            return

        for bc_trans in bc_trans_result.result:
            if bc_trans.data is None:
                continue

            cell = Cell.one_from_boc(bc_trans.data)
            bc_transaction = Transaction.deserialize(cell_slice=cell.begin_parse())

            assert isinstance(bc_transaction, Transaction)

            if bc_transaction.in_msg is None:
                continue

            if not bc_transaction.in_msg.is_external:
                continue

            ext_msg_hash = normalize_hash(bc_transaction.in_msg)

            if ton_transaction.hash != ext_msg_hash:
                continue

            tx_hash = bc_transaction.cell.hash.hex()
            ton_transaction.hash = tx_hash

            log.info(
                "ton_transaction.find_real_hash.found",
                new_hash=tx_hash,
                ext_msg_hash=ext_msg_hash,
                ton_transaction_id=ton_transaction_id,
            )
            return

        log.warning(
            "ton_transaction.find_real_hash.not_found",
            ton_transaction_id=ton_transaction_id,
        )
