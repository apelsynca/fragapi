from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Address, ExternalMessage, to_nano

from src.fee import after_fee, after_ton_network_fee
from src.fragment_transaction.models import FTMetadata
from src.fragment_transaction.repository import FragmentTransactionRepository
from src.fragment_transaction.tasks import process_fragment_transaction
from src.kit.ton_connect import TonConnectTransaction
from src.models import FragmentTransaction, Transaction, User
from src.models.fragment_transactions import FragmentTransactionReason
from src.worker import enqueue_task


class FragmentTransactionService:
    async def buy_stars(
        self,
        session: AsyncSession,
        tc_transaction: TonConnectTransaction,
        user: User,
        recipient: str,
        recipient_username: str,
        stars_amount: int,
    ) -> FragmentTransaction:
        return await self.from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=FragmentTransactionReason.stars,
            metadata=FTMetadata(
                recipient=recipient,
                recipient_username=recipient_username,
                stars_amount=stars_amount,
            ),
        )

    async def gift_premium(
        self,
        session: AsyncSession,
        tc_transaction: TonConnectTransaction,
        user: User,
        recipient: str,
        recipient_username: str,
        premium_months: Literal[3, 6, 12],
    ) -> FragmentTransaction:
        return await self.from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=FragmentTransactionReason.premium,
            metadata=FTMetadata(
                recipient=recipient,
                recipient_username=recipient_username,
                premium_months=premium_months,
            ),
        )

    async def from_tc(
        self,
        session: AsyncSession,
        tc_transaction: TonConnectTransaction,
        user: User,
        reason: FragmentTransactionReason,
        metadata: FTMetadata,
    ) -> FragmentTransaction:
        frag_transaction = await self._create_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=reason,
            metadata=metadata,
        )

        # WARN: maybe there is something better. for now = ideal.
        await session.refresh(user, with_for_update=True)

        user.balance -= frag_transaction.amount

        enqueue_task(
            process_fragment_transaction,
            frag_transaction.id,
            tc_transaction,
        )

        return frag_transaction

    async def _create_from_tc(
        self,
        session: AsyncSession,
        tc_transaction: TonConnectTransaction,
        user: User,
        reason: FragmentTransactionReason,
        metadata: FTMetadata,
    ) -> FragmentTransaction:
        tc_msg = tc_transaction.messages[0]

        ext_msg = ExternalMessage(
            dest=Address(tc_msg.address), body=tc_msg.get_payload_cell()
        )

        # NOTE: move that logic to transaction service
        transaction = Transaction(
            nano_amount=tc_msg.amount,
            hash=None,
            message_hash=ext_msg.normalized_hash,
            from_address=tc_transaction.from_address,
            to_address=Address(tc_msg.address).to_str(is_user_friendly=False),
        )

        without_fee_f_amount = to_nano(tc_msg.amount)
        f_amount = after_fee(after_ton_network_fee(without_fee_f_amount))

        repository = FragmentTransactionRepository.from_session(session)
        transaction = await repository.create(
            FragmentTransaction(
                user=user,
                amount=f_amount,
                recipient=metadata.recipient,
                recipient_username=metadata.recipient_username,
                transaction=transaction,
                reason=reason,
                stars_amount=metadata.stars_amount,
                premium_months=metadata.premium_months,
            )
        )

        return transaction


fragment_transaction = FragmentTransactionService()
