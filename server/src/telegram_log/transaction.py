from ton_core import to_amount

from src.config import settings
from src.enums import TransactionReason
from src.models import TelegramLogsSource, Transaction
from src.telegram_log.tasks import admin_telegram_notification_send, telegram_log_send
from src.worker import enqueue_task

STAR_EMOJI = "⭐️"
GIFT_EMOJI = "🎁"

USER_TELEGRAM_LOG_TEXT = (
    "{head_emoji} <b>Новая транзакция</b>\n\n"
    "Тип: {reason}\n"
    "Сумма: <b>{amount:.4f} TON</b>\n\n"
    "Юзернейм получателя: @{username}\n"
    "Payload: {value}"
)


def enqueue_transaction_telegram_log_task(
    source: TelegramLogsSource,
    transaction: Transaction,
) -> None:
    head_emoji = (
        STAR_EMOJI if transaction.reason == TransactionReason.stars else GIFT_EMOJI
    )

    value_str = "Без payload"
    if transaction.premium_months:
        value_str = f"{transaction.premium_months} месяцев"
    elif transaction.stars_amount:
        value_str = f"{transaction.stars_amount} звезд"

    enqueue_task(
        telegram_log_send,
        chat_id=source.chat_id,
        text=USER_TELEGRAM_LOG_TEXT.format(
            head_emoji=head_emoji,
            amount=transaction.amount,
            reason=transaction.reason,
            username=transaction.recipient_username,
            value=value_str,
        ),
        with_notification=True,
    )


ADMIN_TELEGRAM_TRANSACTION_TITLE_TEMPLATE = (
    "<a href='https://tonscan.org/tx/{hash}'>transaction</a>"
)
ADMIN_TELEGRAM_TRANSACTION_TEXT = (
    "{head_emoji} <b>New {head_title_url}</b>\n\n"
    "User: {user_field}\n"
    "Amount: <b>{amount:.4f} GRAM</b> <i>+{fee_amount:.5f} GRAM</i>\n\n"
    "To username: <i>{username}</i>\n"
    "Payload: <i>{value_str}</i>"
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

    text = ADMIN_TELEGRAM_TRANSACTION_TEXT.format(
        head_emoji=head_emoji,
        head_title_url=ADMIN_TELEGRAM_TRANSACTION_TEXT.format(
            hash=transaction.ton_transaction.hash
        )
        if transaction.ton_transaction.hash
        else "transaction",
        user_field=user_field,
        amount=transaction.amount,
        fee_amount=fee_amount,
        username=f"@{transaction.recipient_username}",
        value_str=value_str,
    )

    with_notification = transaction.amount > settings.MIN_NON_SILENT_AMOUNT

    enqueue_task(
        admin_telegram_notification_send, text=text, with_notification=with_notification
    )
