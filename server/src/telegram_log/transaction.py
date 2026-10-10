from ton_core import to_amount

from src.bot import custom_emoji
from src.config import settings
from src.enums import TransactionReason
from src.models import TelegramLogsSource, Transaction
from src.telegram_log.tasks import admin_telegram_notification_send, telegram_log_send
from src.worker import enqueue_task

USER_TELEGRAM_LOG_TEXT = (
    "{head_emoji} <b>Новая транзакция</b>\n\n"
    "Тип: {reason}\n"
    f"Сумма: <b>{{amount:.4f}} {custom_emoji.GRAM.html}</b>\n\n"
    "Юзернейм получателя: @{username}\n"
    "Payload: {value}"
)


def enqueue_transaction_telegram_log_task(
    source: TelegramLogsSource,
    transaction: Transaction,
) -> None:
    value_str = "Без payload"
    if transaction.premium_months:
        value_str = f"{transaction.premium_months} месяцев"
    elif transaction.stars_amount:
        value_str = f"{transaction.stars_amount} звезд"

    enqueue_task(
        telegram_log_send,
        chat_id=source.chat_id,
        text=USER_TELEGRAM_LOG_TEXT.format(
            head_emoji=_get_head_emoji(transaction.reason),
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
    f"Amount: <b>{{amount:.4f}} {custom_emoji.GRAM.html}</b> "
    f"<i>+{{fee_amount:.5f}} {custom_emoji.GRAM.html}</i>\n\n"
    "To username: <i>{username}</i>\n"
    "Payload: <i>{value_str}</i>"
)


def enqueue_transaction_admin_log_task(transaction: Transaction):
    value_str = "❌ No value"

    if transaction.premium_months:
        value_str = f"{transaction.premium_months} months"
    elif transaction.stars_amount:
        value_str = f"{transaction.stars_amount} stars"

    fee_amount = transaction.amount - float(
        to_amount(transaction.ton_transaction.nano_amount)
    )

    head_title_url = (
        ADMIN_TELEGRAM_TRANSACTION_TITLE_TEMPLATE.format(
            hash=transaction.ton_transaction.hash
        )
        if transaction.ton_transaction.hash
        else "transaction"
    )

    text = ADMIN_TELEGRAM_TRANSACTION_TEXT.format(
        head_emoji=_get_head_emoji(transaction.reason),
        head_title_url=head_title_url,
        user_field=transaction.user.html_telegram_link,
        amount=transaction.amount,
        fee_amount=fee_amount,
        username=f"@{transaction.recipient_username}",
        value_str=value_str,
    )

    with_notification = transaction.amount > settings.MIN_NON_SILENT_AMOUNT

    enqueue_task(
        admin_telegram_notification_send, text=text, with_notification=with_notification
    )


def _get_head_emoji(transaction_reason: TransactionReason) -> str:
    return (
        custom_emoji.TELEGRAM_STAR_ANIMATED.html
        if transaction_reason == TransactionReason.stars
        else custom_emoji.GIFT_ANIMATED.html
    )
