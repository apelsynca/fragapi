from ton_core import to_amount

from src.config import settings
from src.models import FragmentTransaction
from src.models.fragment_transactions import FragmentTransactionReason
from src.worker import enqueue_task

from .tasks import telegram_log_send

STAR_EMOJI = "⭐️"
GIFT_EMOJI = "🎁"

TELEGRAM_LOG_TEXT = (
    "{head_emoji} <b>New transaction</b>\n\n"
    "User: {user_field}\n"
    "Amount: <b>{amount:.4f} TON</b> (<i>+{fee_amount:.4f} TON</i>)\n"
    "Type: {reason}\n\n"
    "Rec-Username: {username}\n"
    "Rec-Value: {value_str}"
)


def enqueue_frag_trans_admin_log_task(fragment_transaction: FragmentTransaction):
    head_emoji = (
        STAR_EMOJI
        if fragment_transaction.reason == FragmentTransactionReason.stars
        else GIFT_EMOJI
    )
    value_str = "❌ No value"

    if fragment_transaction.premium_months:
        value_str = f"{fragment_transaction.premium_months} months"
    elif fragment_transaction.stars_amount:
        value_str = f"{fragment_transaction.stars_amount} stars"

    fee_amount = fragment_transaction.amount - float(
        to_amount(fragment_transaction.transaction.nano_amount)
    )

    user_field = (
        f"<a href='tg://resolve?domain={fragment_transaction.user.username}'>{fragment_transaction.user.first_name}</a>"
        if fragment_transaction.user.username
        else f"<a href='tg://user?id={fragment_transaction.user_id}'>{fragment_transaction.user.first_name}</a>"
    )

    text = TELEGRAM_LOG_TEXT.format(
        head_emoji=head_emoji,
        user_field=user_field,
        amount=fragment_transaction.amount,
        fee_amount=fee_amount,
        reason=fragment_transaction.reason,
        username=f"@{fragment_transaction.recipient_username}",
        value_str=value_str,
    )

    with_notification = fragment_transaction.amount > settings.MIN_NON_SILENT_AMOUNT

    enqueue_task(telegram_log_send, text=text, with_notification=with_notification)
