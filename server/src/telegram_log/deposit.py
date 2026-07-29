from src.models import Deposit
from src.telegram_log.tasks import admin_telegram_notification_send
from src.worker import enqueue_task

NEW_DEPOSIT_NOTIFICATION_TEXT = (
    "💎 <b>New deposit</b>\n\n"
    "User: {user_field}\n"
    "Amount: <b>{amount:.2f} GRAM</b>\n"
    "Balance change: <b>{prev_balance:.2f} GRAM</b> -> <b>{curr_balance:.2f} GRAM</b>\n\n"
    "Ref-Hash: <code>{ref_hash}</code>{ton_transaction_field}"
)
NEW_DEPOSIT_TON_TRANSACTION_TEXT = (
    "\n\n<a href='https://tonscan.org/tx/{}'>Транзакция</a>"
)


def enqueue_new_deposit_admin_log_task(deposit: Deposit) -> None:
    user_field = (
        f"<a href='tg://resolve?domain={deposit.user.username}'>{deposit.user.first_name}</a>"
        if deposit.user.username
        else f"<a href='tg://user?id={deposit.user_id}'>{deposit.user.first_name}</a>"
    )

    ton_transaction_field = (
        NEW_DEPOSIT_TON_TRANSACTION_TEXT.format(deposit.ton_transaction.hash)
        if deposit.ton_transaction
        else ""
    )

    enqueue_task(
        admin_telegram_notification_send,
        text=NEW_DEPOSIT_NOTIFICATION_TEXT.format(
            amount=deposit.amount,
            user_field=user_field,
            ref_hash=deposit.hash,
            ton_transaction_field=ton_transaction_field,
            prev_balance=deposit.user.balance - deposit.amount,
            curr_balance=deposit.user.balance,
        ),
        with_notification=True,
    )
