from pytoniq_core import InternalMsgInfo
from sqlalchemy.ext.asyncio import AsyncSession
from tonutils.utils import to_amount

from src.database.dependencies import DBSession
from src.exceptions import ResourceNotFound
from src.logging import get_logger
from src.openapi import APITag
from src.routing import APIRouter
from src.users.dependencies import UserService, UserServiceDependency

from .main import tonapi_client
from .schemas import TonAPIWebhookMessage

router = APIRouter(prefix="/tonapi", tags=["Webhooks", APITag.private])

log = get_logger()


@router.post("/webhook")
async def webhook(
    message: TonAPIWebhookMessage,
    user_service: UserServiceDependency,
    session: DBSession,
) -> None:
    try:
        await do_shit(message, user_service=user_service, session=session)
    except Exception as exc:
        log.warning("TON API webhook error", error=str(exc))


async def do_shit(
    message: TonAPIWebhookMessage, user_service: UserService, session: AsyncSession
):
    transaction = await tonapi_client.get_transaction(hash=message.tx_hash)
    if transaction.in_msg is None:
        log.warning("Transaction without internal message!")
        return

    if not isinstance(transaction.in_msg.info, InternalMsgInfo):
        return

    if len(transaction.in_msg.body.bits) == 0:  # empty msg.
        log.warning("Skipping transaction without data")
        return

    cs = transaction.in_msg.body.begin_parse()
    op_code = cs.load_uint(32)
    if op_code != 0:
        log.warning("Skipping non-comment transaction")
        return

    amount = to_amount(transaction.in_msg.info.value.grams)
    comment = cs.load_snake_string()

    log.debug("New wallet transaction!", amount=amount, comment=comment)

    if not comment.isdigit():
        log.warning("Transaction with non-digit comment")
        return

    try:
        user = await user_service.get(id=int(comment))
    except ResourceNotFound:
        log.info("Cannot find user for top-up", amount=amount, comment=comment)
        return

    log.info(
        "User balance top-up",
        user_id=user.id,
        amount=amount,
        prev_balance=user.balance,
        new_balance=user.balance + amount,
    )

    user.balance += amount
    await session.commit()
