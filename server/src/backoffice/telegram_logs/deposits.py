from src.backoffice.telegram_logs.tasks import telegram_log_send
from src.models import Deposit
from src.worker import enqueue_task

NEW_DEPOSIT_NOTIFICATION_TEXT = (
    "💎 <b>New deposit</b>\n\n"
    "User: {user_field}\n"
    "Amount: <b>{amount:.2f} GRAM</b>\n\n"
    "Ref-Hash: <code>{ref_hash}</code>"
)


def enqueue_new_deposit_admin_log_task(deposit: Deposit) -> None:
    user_field = (
        f"<a href='tg://resolve?domain={deposit.user.username}'>{deposit.user.first_name}</a>"
        if deposit.user.username
        else f"<a href='tg://user?id={deposit.user_id}'>{deposit.user.first_name}</a>"
    )

    enqueue_task(
        telegram_log_send,
        text=NEW_DEPOSIT_NOTIFICATION_TEXT.format(
            amount=deposit.amount, user_field=user_field, ref_hash=deposit.hash
        ),
        with_notification=True,
    )
