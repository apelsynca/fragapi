from uuid import UUID

from sqlalchemy.orm import selectinload

from src.bot.logs_sender import telegram_log_sender
from src.config import settings
from src.exceptions import ResourceNotFound
from src.fragment_transaction.repository import FragmentTransactionRepository
from src.models.fragment_transactions import (
    FragmentTransaction,
    FragmentTransactionReason,
)
from src.worker import broker
from src.worker._sqlalchemy import AsyncSessionMaker

STAR_EMOJI = "⭐️"
GIFT_EMOJI = "🎁"

NOTIFICATION_TEXT = (
    "{head_emoji} <b>New transaction</b>\n\n"
    "User: <a href='tg://user?id={user_id}'>{first_name}</a>\n"
    "Amount: {amount} TON (+{before_fee_amount} TON)\n"
    "Type: {reason}\n\n"
    "R-Username: {username}"
    "R-Value: {value_str}"
)


@broker.task
async def send_telegram_log(fragment_transaction_id: UUID) -> None:
    async with AsyncSessionMaker() as session:
        repository = FragmentTransactionRepository.from_session(session)
        fragment_transaction = await repository.get_by_id(
            id=fragment_transaction_id, options=[selectinload(FragmentTransaction.user)]
        )

        if fragment_transaction is None:
            raise ResourceNotFound()

        head_emoji = (
            STAR_EMOJI
            if fragment_transaction.reason == FragmentTransactionReason.stars
            else GIFT_EMOJI
        )
        value_str = "❌ No value"
        if fragment_transaction.premium_months:
            value_str = f"{fragment_transaction.premium_months} months"
        elif fragment_transaction.star_amount:
            value_str = f"{fragment_transaction.star_amount} stars"
        text = NOTIFICATION_TEXT.format(
            head_emoji=head_emoji,
            user_id=fragment_transaction.user_id,
            first_name=fragment_transaction.user.first_name,
            amount=fragment_transaction.amount,
            before_fee_amount=fragment_transaction.amount,
            reason=fragment_transaction.reason,
            username=fragment_transaction.username,
            value_str=value_str,
        )

        with_notification = fragment_transaction.amount > settings.MIN_NON_SILENT_AMOUNT

        await telegram_log_sender.send(
            text=text,
            with_notification=with_notification,
        )
