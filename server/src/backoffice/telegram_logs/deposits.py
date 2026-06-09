from src.backoffice.telegram_logs.tasks import telegram_log_send
from src.models import Payment
from src.worker import enqueue_task

NEW_DEPOSIT_NOTIFICATION_TEXT = (
    "💎 <b>New deposit</b>\n\n"
    "User: {user_field}\n"
    "Amount: <b>{amount:.2f} TON</b>\n\n"
    "Hash: <code>{hash}</code>"
)


def enqueue_new_deposit_admin_log_task(payment: Payment) -> None:
    user_field = (
        f"<a href='tg://resolve?domain={payment.user.username}'>{payment.user.first_name}</a>"
        if payment.user.username
        else f"<a href='tg://user?id={payment.user_id}'>{payment.user.first_name}</a>"
    )

    enqueue_task(
        telegram_log_send,
        text=NEW_DEPOSIT_NOTIFICATION_TEXT.format(
            amount=payment.amount, user_field=user_field, hash=payment.hash
        ),
        with_notification=True,
    )
