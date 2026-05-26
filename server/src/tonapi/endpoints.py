import structlog
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragError
from src.logging import Logger
from src.openapi import APITag
from src.postgres import get_db_session
from src.routing import APIRouter
from src.tonapi.schemas import TonAPIWebhookMessage
from src.tonapi.service import tonapi as tonapi_service

router = APIRouter(prefix="/tonapi", tags=[APITag.private])

log: Logger = structlog.get_logger()


@router.post("/webhook")
async def tonapi_webhook(
    message: TonAPIWebhookMessage, session: AsyncSession = Depends(get_db_session)
) -> None:
    log.info(
        "Tonapi webhook message",
        event_type=message.event_type,
        account_id=message.account_id,
        lt=message.lt,
        tx_hash=message.tx_hash,
    )

    if message.event_type == "account_tx":
        try:
            await tonapi_service.process_webhook_acc_tx(
                session=session, webhook_message=message
            )
        except FragError as exc:
            log.warn("TonAPI webhook internal error", error=str(exc))
        except Exception as exc:
            log.error("TonAPI webhook unknown error", error=str(exc))
