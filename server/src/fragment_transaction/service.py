from collections.abc import Sequence
from datetime import timedelta

import structlog
from sqlalchemy import case, func, select
from ton_core import to_amount

from src.exceptions import InsuficcientFunds
from src.fee import after_fee, after_ton_network_fee
from src.fragment_transaction.models import FTMetadata
from src.fragment_transaction.repository import FragmentTransactionRepository
from src.fragment_transaction.schemas import ChartPoint, FragmentTransactionsStats
from src.fragment_transaction.sorting import FragTransactionSortProperty
from src.fragment_transaction.tasks import process_fragment_transaction
from src.fragment_transaction.utils import validate_tc_transaction
from src.kit.pagination import PaginationParams
from src.kit.sorting import Sorting
from src.kit.ton_connect import TonConnectTransaction
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import FragmentTransaction, User
from src.models.fragment_transactions import FragmentTransactionReason
from src.postgres import AsyncSession
from src.ton_transaction.service import transaction as transaction_service
from src.worker import enqueue_task

log: Logger = structlog.get_logger()


class FragmentTransactionService:
    async def get_stats(
        self, session: AsyncSession, user: User
    ) -> FragmentTransactionsStats:
        stmt = select(
            func.sum(FragmentTransaction.amount).label("total_amount"),
            func.sum(
                case(
                    (
                        FragmentTransaction.reason == FragmentTransactionReason.stars,
                        FragmentTransaction.amount,
                    ),
                    else_=0,
                )
            ).label("stars_total_amount"),
            func.sum(
                case(
                    (
                        FragmentTransaction.reason == FragmentTransactionReason.premium,
                        FragmentTransaction.amount,
                    ),
                    else_=0,
                )
            ).label("premium_total_amount"),
        ).where(FragmentTransaction.user == user)
        result = await session.execute(stmt)
        row = result.one()

        return FragmentTransactionsStats(
            total_spend=row.total_amount or 0,
            stars_total_spend=row.stars_total_amount or 0,
            premium_total_spend=row.premium_total_amount or 0,
        )

    async def fetch_list(
        self,
        session: AsyncSession,
        user: User,
        pagination: PaginationParams,
        sorting: list[Sorting[FragTransactionSortProperty]] = [
            (FragTransactionSortProperty.created_at, True)
        ],
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
        fragment_transaction = await self._create_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=reason,
            metadata=metadata,
        )

        # WARN: maybe there is something better. for now = ideal.
        await session.refresh(user, with_for_update=True)

        if user.balance <= fragment_transaction.amount:
            # NOTE: frag trans unsaved here, which is good.
            raise InsuficcientFunds(required_amount=fragment_transaction.amount)

        user.balance -= fragment_transaction.amount

        log.info(
            "fragment_transaction.send_from_tc",
            fragment_transaction_id=fragment_transaction.id,
        )

        enqueue_task(
            process_fragment_transaction,
            fragment_transaction.id,
            tc_transaction,
        )

        return fragment_transaction

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

        transaction = await transaction_service.create_as_tc(
            session=session, tc_transaction=tc_transaction
        )

        without_fee_f_amount = float(to_amount(tc_msg.amount))
        f_amount = after_fee(after_ton_network_fee(without_fee_f_amount))

        repository = FragmentTransactionRepository.from_session(session)
        fragment_transaction = await repository.create(
            FragmentTransaction(
                user=user,
                amount=f_amount,
                recipient=metadata.recipient,
                recipient_username=metadata.recipient_username,
                ton_transaction=transaction,
                reason=reason,
                stars_amount=metadata.stars_amount,
                premium_months=metadata.premium_months,
            )
        )

        return fragment_transaction

    async def get_chart_data(
        self, session: AsyncSession, user: User
    ) -> list[ChartPoint]:
        days_count = 90

        today = utc_now().date()
        start_date = today - timedelta(days=days_count - 1)

        stmt = (
            select(
                func.date(FragmentTransaction.created_at).label("date"),
                func.sum(
                    case(
                        (
                            FragmentTransaction.reason == "stars",
                            FragmentTransaction.amount,
                        ),
                        else_=0,
                    ).label("stars_spend")
                ),
                func.sum(
                    case(
                        (
                            FragmentTransaction.reason == "premium",
                            FragmentTransaction.amount,
                        ),
                        else_=0,
                    ).label("premium_spend")
                ),
            )
            .where(
                FragmentTransaction.user == user,
                FragmentTransaction.reason == FragmentTransactionReason.stars,
                # FragmentTransaction.created_at # NOTE might do that lol
            )
            .group_by(func.date(FragmentTransaction.created_at))
        )

        result = await session.execute(stmt)
        rows = result.all()

        existing = {row.date: row for row in rows}

        result = []

        for i in range(days_count):
            day = start_date + timedelta(days=i)
            row = existing.get(day, None)

            if row is None:
                result.append(ChartPoint(date=day, stars_spend=0, premium_spend=0))
                continue

            log.debug("row at the row the row is row", row=row)

            result.append(
                ChartPoint(
                    date=day,
                    stars_spend=row[1],
                    premium_spend=row[2],
                )
            )

        return result


fragment_transaction = FragmentTransactionService()
