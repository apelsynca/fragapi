from ton_core import to_amount

from src.bot import custom_emoji
from src.config import settings
from src.enums import TransactionReason
from src.models import TelegramLogsSource, Transaction
from src.telegram_log.tasks import admin_telegram_notification_send, telegram_log_send
from src.worker import enqueue_task

# Telegram allows 4096 characters per message; 50 recipient lines stay well under.
BULK_LINES_PER_MESSAGE = 50

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


USER_TELEGRAM_BULK_LOG_TEXT = (
    "{head_emoji} <b>Новая транзакция</b>\n\n"
    "Тип: {reason}\n"
    "Покупок: <b>{count}</b>\n"
    f"Сумма: <b>{{amount:.4f}} {custom_emoji.GRAM.html}</b>\n"
    "{total_field}\n"
    "Получатели:\n"
    "<blockquote>{recipients}</blockquote>"
)
USER_TELEGRAM_BULK_LOG_NEXT_TEXT = (
    "{head_emoji} <b>Транзакция</b> · {part}/{parts}\n\n"
    "<blockquote>{recipients}</blockquote>"
)


def enqueue_bulk_transaction_telegram_log_tasks(
    source: TelegramLogsSource,
    transactions: list[Transaction],
) -> None:
    """One digest for the whole bulk, so the chat is not flooded per purchase."""
    head_emoji = _get_head_emoji(transactions[0].reason)
    stars_total = sum(t.stars_amount or 0 for t in transactions)
    chunks = _recipient_chunks(
        [f"@{t.recipient_username} — {_user_value_str(t)}" for t in transactions]
    )

    for part, recipients in enumerate(chunks, start=1):
        if part == 1:
            text = USER_TELEGRAM_BULK_LOG_TEXT.format(
                head_emoji=head_emoji,
                reason=transactions[0].reason,
                count=len(transactions),
                amount=sum(t.amount for t in transactions),
                total_field=(
                    f"Всего: <b>{_format_number(stars_total)} звезд</b>\n"
                    if stars_total
                    else ""
                ),
                recipients=recipients,
            )
        else:
            text = USER_TELEGRAM_BULK_LOG_NEXT_TEXT.format(
                head_emoji=head_emoji,
                part=part,
                parts=len(chunks),
                recipients=recipients,
            )

        enqueue_task(
            telegram_log_send,
            chat_id=source.chat_id,
            text=text,
            # Only the first part pings, the rest follow silently.
            with_notification=part == 1,
        )


ADMIN_TELEGRAM_BULK_TRANSACTION_TEXT = (
    "{head_emoji} <b>New bulk {head_title_url}</b> · {count} purchases\n\n"
    "User: {user_field}\n"
    f"Amount: <b>{{amount:.4f}} {custom_emoji.GRAM.html}</b> "
    f"<i>+{{fee_amount:.5f}} {custom_emoji.GRAM.html}</i>\n"
    "{total_field}\n"
    "Recipients:\n"
    "<blockquote>{recipients}</blockquote>"
)
ADMIN_TELEGRAM_BULK_TRANSACTION_NEXT_TEXT = (
    "{head_emoji} <b>Bulk transaction</b> · {part}/{parts}\n\n"
    "<blockquote>{recipients}</blockquote>"
)


def enqueue_bulk_transaction_admin_log_tasks(transactions: list[Transaction]) -> None:
    """One digest for the whole bulk, so the admin chat is not flooded per purchase."""
    first = transactions[0]
    head_emoji = _get_head_emoji(first.reason)
    amount = sum(t.amount for t in transactions)
    fee_amount = amount - sum(
        float(to_amount(t.ton_transaction.nano_amount)) for t in transactions
    )
    stars_total = sum(t.stars_amount or 0 for t in transactions)
    chunks = _recipient_chunks(
        [f"@{t.recipient_username} — {_admin_value_str(t)}" for t in transactions]
    )

    for part, recipients in enumerate(chunks, start=1):
        if part == 1:
            text = ADMIN_TELEGRAM_BULK_TRANSACTION_TEXT.format(
                head_emoji=head_emoji,
                head_title_url=(
                    ADMIN_TELEGRAM_TRANSACTION_TITLE_TEMPLATE.format(
                        hash=first.ton_transaction.hash
                    )
                    if first.ton_transaction.hash
                    else "transaction"
                ),
                count=len(transactions),
                user_field=first.user.html_telegram_link,
                amount=amount,
                fee_amount=fee_amount,
                total_field=(
                    f"Total: <b>{_format_number(stars_total)} stars</b>\n"
                    if stars_total
                    else ""
                ),
                recipients=recipients,
            )
        else:
            text = ADMIN_TELEGRAM_BULK_TRANSACTION_NEXT_TEXT.format(
                head_emoji=head_emoji,
                part=part,
                parts=len(chunks),
                recipients=recipients,
            )

        enqueue_task(
            admin_telegram_notification_send,
            text=text,
            # Only the first part may ping, the rest follow silently.
            with_notification=part == 1 and amount > settings.MIN_NON_SILENT_AMOUNT,
        )


def _recipient_chunks(lines: list[str]) -> list[str]:
    """Numbers the lines and joins them into per-message blocks."""
    numbered = [f"{number}. {line}" for number, line in enumerate(lines, start=1)]
    return [
        "\n".join(numbered[start : start + BULK_LINES_PER_MESSAGE])
        for start in range(0, len(numbered), BULK_LINES_PER_MESSAGE)
    ]


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _user_value_str(transaction: Transaction) -> str:
    if transaction.premium_months:
        return f"{transaction.premium_months} месяцев"
    if transaction.stars_amount:
        return f"{_format_number(transaction.stars_amount)} звезд"
    return "Без payload"


def _admin_value_str(transaction: Transaction) -> str:
    if transaction.premium_months:
        return f"{transaction.premium_months} months"
    if transaction.stars_amount:
        return f"{_format_number(transaction.stars_amount)} stars"
    return "❌ No value"


def _get_head_emoji(transaction_reason: TransactionReason) -> str:
    return (
        custom_emoji.TELEGRAM_STAR_ANIMATED.html
        if transaction_reason == TransactionReason.stars
        else custom_emoji.GIFT_ANIMATED.html
    )
