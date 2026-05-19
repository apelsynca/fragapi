import uuid

from sqlalchemy.orm import selectinload

from src.bot.logs_sender import telegram_log_sender
from src.exceptions import ResourceNotFound
from src.models import Payment
from src.payment.repository import PaymentRepository
from src.worker import AsyncSessionMaker, broker

TXT_TEMP = (
    "<b>New deposit</b>\n\n"
    "Amount: <b>{amount:.4f} TON</b>\n"
    "UserID: {user_id}\n\n"
    "{status}"
)


@broker.task
async def deposit_send_telegram_log(payment_id: uuid.UUID) -> None:
    async with AsyncSessionMaker() as session:
        repository = PaymentRepository.from_session(session)
        payment = await repository.get_by_id(
            id=payment_id, options=[selectinload(Payment.user)]
        )

        if payment is None:
            raise ResourceNotFound()

        await telegram_log_sender.send(
            text=TXT_TEMP.format(
                amount=payment.amount,
                user_id=payment.user_id,
                status=str(payment.status),
            ),
            with_notification=True,
        )
