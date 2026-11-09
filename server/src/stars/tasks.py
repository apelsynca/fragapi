import uuid
from typing import Annotated

import structlog
from taskiq import TaskiqDepends

from src.enums import BulkPurchaseStatus
from src.exceptions import ResourceNotFound
from src.integrations.fragment import Fragment
from src.kit.ton_connect import TonConnectTransaction
from src.logging import Logger
from src.models import StarsBulkPurchase
from src.postgres import AsyncSession
from src.redis import Redis
from src.stars.service import stars as stars_service
from src.transaction.tasks import process_purchases
from src.wallet.manager import WalletManager
from src.wallet.send_gate import WalletSendGate
from src.worker import worker_task_with_queue_manager
from src.worker.fragment import get_fragment
from src.worker.redis import get_worker_redis
from src.worker.sqlalchemy import get_async_session
from src.worker.wallet_manager import get_wallet_manager
from src.worker.wallet_send_gate import get_wallet_send_gate

log: Logger = structlog.get_logger()


@worker_task_with_queue_manager(
    task_name="stars.bulk_purchase_process", retry_on_error=True, max_retries=3
)
async def stars_bulk_purchase_process(
    bulk_purchase_id: uuid.UUID,
    session: Annotated[AsyncSession, TaskiqDepends(get_async_session)],
    fragment: Annotated[Fragment, TaskiqDepends(get_fragment)],
    redis: Annotated[Redis, TaskiqDepends(get_worker_redis)],
    wallet_manager: Annotated[WalletManager, TaskiqDepends(get_wallet_manager)],
    send_gate: Annotated[WalletSendGate, TaskiqDepends(get_wallet_send_gate)],
) -> None:
    """
    Resolves, charges and sends a stars bulk purchase. Each phase is recorded in
    `status`, so a retry continues where it stopped and never charges twice.
    """
    bulk = await session.get(StarsBulkPurchase, bulk_purchase_id)
    if bulk is None:
        raise ResourceNotFound()

    if bulk.status == BulkPurchaseStatus.pending:
        await stars_service.charge_bulk(
            session=session, bulk=bulk, fragment=fragment, redis=redis
        )

    if bulk.status != BulkPurchaseStatus.charged:
        return

    charged = [item for item in bulk.items if item.get("transaction_id")]
    if charged:
        await process_purchases(
            session,
            [uuid.UUID(item["transaction_id"]) for item in charged],
            [
                TonConnectTransaction.model_validate(item["tc_transaction"])
                for item in charged
            ],
            wallet_manager,
            send_gate,
        )

    bulk.status = BulkPurchaseStatus.done
    await session.commit()
    log.info("stars.bulk_purchase_process.done", charged_count=len(charged))
