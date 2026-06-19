from ton_core import to_amount

from src.config import settings
from src.enums import TransactionReason
from src.models import Transaction
from src.worker import enqueue_task

from .tasks import telegram_log_send

STAR_EMOJI = "⭐️"
GIFT_EMOJI = "🎁"

TELEGRAM_LOG_TEXT = (
    "{head_emoji} <b>New transaction</b>\n\n"
    "User: {user_field}\n"
    "Amount: <b>{amount:.4f} GRAM</b> (<i>+{fee_amount:.4f} GRAM</i>)\n"
    "Type: {reason}\n\n"
    "Rec-Username: {username}\n"
    "Rec-Value: {value_str}"
)


def enqueue_transaction_admin_log_task(transaction: Transaction):
    head_emoji = (
        STAR_EMOJI if transaction.reason == TransactionReason.stars else GIFT_EMOJI
    )
    value_str = "❌ No value"

    if transaction.premium_months:
        value_str = f"{transaction.premium_months} months"
    elif transaction.stars_amount:
        value_str = f"{transaction.stars_amount} stars"

    fee_amount = transaction.amount - float(
        to_amount(transaction.ton_transaction.nano_amount)
    )

    user_field = (
        f"<a href='tg://resolve?domain={transaction.user.username}'>{transaction.user.first_name}</a>"
        if transaction.user.username
        else f"<a href='tg://user?id={transaction.user_id}'>{transaction.user.first_name}</a>"
    )

    text = TELEGRAM_LOG_TEXT.format(
        head_emoji=head_emoji,
        user_field=user_field,
        amount=transaction.amount,
        fee_amount=fee_amount,
        reason=transaction.reason,
        username=f"@{transaction.recipient_username}",
        value_str=value_str,
    )

    with_notification = transaction.amount > settings.MIN_NON_SILENT_AMOUNT

    enqueue_task(telegram_log_send, text=text, with_notification=with_notification)
