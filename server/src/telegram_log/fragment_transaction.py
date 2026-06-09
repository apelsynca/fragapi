from src.models import FragmentTransaction, TelegramLogsSource
from src.models.fragment_transactions import FragmentTransactionReason
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


async def enqueu_new_trans_telegram_log_task(
    source: TelegramLogsSource,
    fragment_transaction: FragmentTransaction,
) -> None:
    head_emoji = (
        STAR_EMOJI
        if fragment_transaction.reason == FragmentTransactionReason.stars
        else GIFT_EMOJI
    )

    value_str = "Без подгрузочки"
    if fragment_transaction.premium_months:
        value_str = f"{fragment_transaction.premium_months} месяцев"
    elif fragment_transaction.stars_amount:
        value_str = f"{fragment_transaction.stars_amount} звезд"

    enqueue_task(
        telegram_log_send,
        chat_id=source.chat_id,
        text=USER_TELEGRAM_LOG_TEXT.format(
            head_emoji=head_emoji,
            amount=fragment_transaction.amount,
            reason=fragment_transaction.reason,
            username=fragment_transaction.recipient_username,
            value=value_str,
        ),
        with_notification=True,  # NOTE: might change to custom setting, or range setting
    )
