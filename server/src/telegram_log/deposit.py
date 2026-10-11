from src.bot import custom_emoji
from src.models import Deposit
from src.telegram_log.tasks import admin_telegram_notification_send
from src.worker import enqueue_task

NEW_DEPOSIT_NOTIFICATION_TEXT = (
    f"{custom_emoji.PLUS_ANIMATED.html} <b>New deposit</b>\n\n"
    "User: {user_field}\n"
    f"Amount: <b>{{amount:.2f}}</b> {custom_emoji.GRAM.html}\n"
    f"Balance change: <b>{{prev_balance:.2f}} {custom_emoji.GRAM.html}</b> "
    f"-> <b>{{curr_balance:.2f}} {custom_emoji.GRAM.html}</b>\n\n"
    "Ref-Hash: <code>{ref_hash}</code>{ton_transaction_field}"
)
NEW_DEPOSIT_TON_TRANSACTION_TEXT = (
    "\n\n<a href='https://tonscan.org/tx/{}'>Транзакция</a>"
)


def enqueue_new_deposit_admin_log_task(deposit: Deposit) -> None:
    ton_transaction_field = (
        NEW_DEPOSIT_TON_TRANSACTION_TEXT.format(deposit.ton_transaction.hash)
        if deposit.ton_transaction
        else ""
    )

    enqueue_task(
        admin_telegram_notification_send,
        text=NEW_DEPOSIT_NOTIFICATION_TEXT.format(
            amount=deposit.amount,
            user_field=deposit.user.html_telegram_link,
            ref_hash=deposit.hash,
            ton_transaction_field=ton_transaction_field,
            prev_balance=deposit.user.balance - deposit.amount,
            curr_balance=deposit.user.balance,
        ),
        with_notification=True,
    )
