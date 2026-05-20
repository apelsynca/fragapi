from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Address, ExternalMessage, to_amount

from src.exceptions import InsuficcientFunds
from src.fee import after_fee, after_ton_network_fee
from src.fragment_transaction import sorting
from src.fragment_transaction.models import FTMetadata
from src.fragment_transaction.repository import FragmentTransactionRepository
from src.fragment_transaction.tasks import process_fragment_transaction
from src.fragment_transaction.utils import validate_tc_transaction
from src.kit.pagination import PaginationParams
from src.kit.ton_connect import TonConnectTransaction
from src.models import FragmentTransaction, Transaction, User
from src.models.fragment_transactions import FragmentTransactionReason
from src.worker import enqueue_task


class FragmentTransactionService:
    async def fetch_list(
        self,
        session: AsyncSession,
        user: User,
        pagination: PaginationParams,
        sorting: sorting.ListSorting,
    ) -> tuple[Sequence[FragmentTransaction], int]:
        repository = FragmentTransactionRepository.from_session(session)

        stmt = repository.get_base_stmt().where(FragmentTransaction.user == user)
        stmt = repository.apply_sorting(stmt=stmt, sorting=sorting)

        return await repository.paginate(
            stmt=stmt, limit=pagination.limit, page=pagination.page
        )

    async def send_from_tc(
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

        if user.balance <= frag_transaction.amount:
            raise InsuficcientFunds(amount=user.balance)

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
        validate_tc_transaction(tc_transaction)

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

        # NOTE: jumper.
        without_fee_f_amount = float(to_amount(tc_msg.amount))
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
