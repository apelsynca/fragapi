import uuid

from sqlalchemy.orm import selectinload

from src.bot.logs_sender import telegram_log_sender
from src.exceptions import ResourceNotFound
from src.models import Payment
from src.payment.repository import PaymentRepository
from src.worker import AsyncSessionMaker, broker

NEW_DEPOSIT_NOTIFICATION_TEXT = (
    "<b>New deposit</b>\n\n"
    "User: {user_field}\n"
    "Amount: <b>{amount:.4f} TON</b>\n\n"
    "Hash: <code>{hash}</code>"
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

        user_field = (
            f"<a href='tg://resolve?domain={payment.user.username}'>{payment.user.first_name}</a>"
            if payment.user.username
            else f"<a href='tg://user?id={payment.user_id}'>{payment.user.first_name}</a>"
        )

        await telegram_log_sender.send(
            text=NEW_DEPOSIT_NOTIFICATION_TEXT.format(
                amount=payment.amount, user_field=user_field, hash=payment.hash
            ),
            with_notification=True,
        )
