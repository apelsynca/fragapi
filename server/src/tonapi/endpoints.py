from src.logging import get_logger
from src.openapi import APITag
from src.routing import APIRouter
from src.tonapi.schemas import TonAPIWebhookMessage
from src.tonapi.service import tonapi as tonapi_service

router = APIRouter(prefix="/tonapi", tags=[APITag.private])

log = get_logger()


@router.post("/webhook")
async def tonapi_webhook(message: TonAPIWebhookMessage) -> None:
    log.debug("Tonapi webhook message", message=message)

    if message.event_type == "account_tx":
        await tonapi_service.process_webhook_account_tx_message(message=message)
