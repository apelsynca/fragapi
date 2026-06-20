from src.enums import TransactionReason
from src.models import TelegramLogsSource, Transaction
from src.telegram_log.tasks import telegram_log_send
from src.worker import enqueue_task

STAR_EMOJI = "⭐️"
GIFT_EMOJI = "🎁"

USER_TELEGRAM_LOG_TEXT = (
    "{head_emoji} <b>Новая транзакция</b>\n\n"
    "Тип: {reason}\n"
    "Сумма: <b>{amount:.2f} TON</b>\n\n"
    "Юзернейм получателя: @{username}\n"
    "Нагрузка транзакции: {value}"
)


def enqueue_transaction_telegram_log_task(
    source: TelegramLogsSource,
    transaction: Transaction,
) -> None:
    head_emoji = (
        STAR_EMOJI if transaction.reason == TransactionReason.stars else GIFT_EMOJI
    )

    value_str = "Без подгрузочки"
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
