import uuid

import structlog
from sqlalchemy.orm import selectinload
from ton_core import Address, ExternalMessage, WalletV5Params, to_amount

from src.bot.logs_sender import telegram_log_sender
from src.config import settings
from src.exceptions import BadRequest, ResourceNotFound
from src.fragment_transaction.repository import FragmentTransactionRepository
from src.fragment_transaction.utils import validate_tc_transaction
from src.kit.ton_connect import TonConnectTransaction
from src.logging import Logger
from src.models.fragment_transactions import (
    FragmentTransaction,
    FragmentTransactionReason,
)
from src.worker import broker
from src.worker._sqlalchemy import AsyncSessionMaker
from src.worker._wallet_manager import WalletManagerMiddleware

log: Logger = structlog.get_logger()


@broker.task
async def process_fragment_transaction(
    fragment_transaction_id: uuid.UUID, tc_transaction: TonConnectTransaction
) -> None:
    validate_tc_transaction(tc_transaction=tc_transaction)

    log.info(
        "Processing new fragment transaction",
        fragment_transaction_id=fragment_transaction_id,
    )
    log.debug(
        "TC Transaction",
        fragment_transaction_id=fragment_transaction_id,
        tc_transaction=tc_transaction,
    )

    async with AsyncSessionMaker() as session:
        repository = FragmentTransactionRepository.from_session(session)
        fragment_transaction = await repository.get_by_id(
            id=fragment_transaction_id,
            options=[
                selectinload(FragmentTransaction.user),
                selectinload(FragmentTransaction.transaction),
            ],
        )

        if fragment_transaction is None:
            raise ResourceNotFound()

        log.info(
            "Processing transaction",
            user=fragment_transaction.user,
            amount=fragment_transaction.amount,
            recipient_username=fragment_transaction.recipient_username,
            stars_amount=fragment_transaction.stars_amount,
            premium_months=fragment_transaction.premium_months,
        )

        tc_msg = tc_transaction.messages[0]
        ext_msg = ExternalMessage(
            dest=Address(tc_msg.address), body=tc_msg.get_payload_cell()
        )

        if fragment_transaction.transaction.message_hash != ext_msg.normalized_hash:
            raise BadRequest("Hash is bad")

        wallet_manager = WalletManagerMiddleware.get()

        async with wallet_manager:
            wallet = await wallet_manager.get_wallet_for_amount(amount=tc_msg.amount)

            body = tc_msg.get_payload_cell()
            valid_until = int(tc_transaction.valid_until.timestamp()) + 10

            ext_msg = await wallet.transfer(
                destination=Address(tc_msg.address),
                body=body,
                amount=tc_msg.amount,
                params=WalletV5Params(valid_until=valid_until),
            )

        fragment_transaction.transaction.hash = ext_msg.normalized_hash

        await send_telegram_log.kiq(fragment_transaction_id=fragment_transaction.id)


STAR_EMOJI = "⭐️"
GIFT_EMOJI = "🎁"

NOTIFICATION_TEXT = (
    "{head_emoji} <b>New transaction</b>\n\n"
    "User: {user_field}\n"
    "Amount: <b>{amount:.4f} TON</b> (<i>+{fee_amount:.4f} TON</i>)\n"
    "Type: {reason}\n\n"
    "R-Username: {username}\n"
    "R-Value: {value_str}"
)


@broker.task
async def send_telegram_log(fragment_transaction_id: uuid.UUID) -> None:
    async with AsyncSessionMaker() as session:
        repository = FragmentTransactionRepository.from_session(session)
        fragment_transaction = await repository.get_by_id(
            id=fragment_transaction_id,
            options=[
                selectinload(FragmentTransaction.user),
                selectinload(FragmentTransaction.transaction),
            ],
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

        text = NOTIFICATION_TEXT.format(
            head_emoji=head_emoji,
            user_field=user_field,
            amount=fragment_transaction.amount,
            fee_amount=fee_amount,
            reason=fragment_transaction.reason,
            username=f"@{fragment_transaction.recipient_username}",
            value_str=value_str,
        )

        with_notification = fragment_transaction.amount > settings.MIN_NON_SILENT_AMOUNT

        await telegram_log_sender.send(
            text=text,
            with_notification=with_notification,
        )
