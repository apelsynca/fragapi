# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.logging import get_logger
# from src.openapi import APITag
# from src.postgres import get_db_session
# from src.routing import APIRouter
# from src.tonapi.schemas import TonAPIWebhookMessage
# from src.tonapi.service import tonapi as tonapi_service
#
# router = APIRouter(prefix="/tonapi", tags=[APITag.private])
#
# log = get_logger()
#
#
# @router.post("/webhook")
# async def tonapi_webhook(
#     message: TonAPIWebhookMessage, session: AsyncSession = Depends(get_db_session)
# ) -> None:
#     log.info("Tonapi webhook message", message=message)
#
#     if message.event_type == "account_tx":
#         try:
#             await tonapi_service.process_webhook_account_tx_message(
#                 session=session, message=message
#             )
#         except Exception as exc:
#             log.error("Deposit error", error=str(exc))
