from collections.abc import Sequence
from datetime import timedelta

import structlog
from sqlalchemy import case, func, select
from ton_core import to_amount

from src.enums import TransactionReason
from src.exceptions import InsuficcientFunds
from src.fee import after_fee, after_ton_network_fee
from src.kit.pagination import PaginationParams
from src.kit.sorting import Sorting
from src.kit.ton_connect import TonConnectTransaction
from src.kit.utils import utc_now
from src.logging import Logger
from src.models import Transaction, User
from src.postgres import AsyncSession
from src.ton_transaction.service import ton_transaction as ton_transaction_service
from src.transaction.models import FTMetadata
from src.transaction.repository import TransactionRepository
from src.transaction.schemas import ChartPoint, TransactionStats
from src.transaction.sorting import TransactionSortProperty
from src.transaction.tasks import fragment_transaction_process
from src.transaction.utils import validate_tc_transaction
from src.worker import enqueue_task

log: Logger = structlog.get_logger()


class TransactionService:
    async def get_stats(self, session: AsyncSession, user: User) -> TransactionStats:
        stmt = select(
            func.sum(Transaction.amount).label("total_amount"),
            func.sum(
                case(
                    (
                        Transaction.reason == TransactionReason.stars,
                        Transaction.amount,
                    ),
                    else_=0,
                )
            ).label("stars_total_amount"),
            func.sum(
                case(
                    (
                        Transaction.reason == TransactionReason.premium,
                        Transaction.amount,
                    ),
                    else_=0,
                )
            ).label("premium_total_amount"),
        ).where(Transaction.user == user)
        result = await session.execute(stmt)
        row = result.one()

        return TransactionStats(
            total_spend=row.total_amount or 0,
            stars_total_spend=row.stars_total_amount or 0,
            premium_total_spend=row.premium_total_amount or 0,
        )

    async def fetch_list(
        self,
        session: AsyncSession,
        user: User,
        pagination: PaginationParams,
        sorting: list[Sorting[TransactionSortProperty]] = [
            (TransactionSortProperty.created_at, True)
        ],
    ) -> tuple[Sequence[Transaction], int]:
        repository = TransactionRepository.from_session(session)

        stmt = repository.apply_sorting(
            stmt=repository.get_base_stmt().where(Transaction.user == user),
            sorting=sorting,
        )

        return await repository.paginate(
            stmt=stmt, limit=pagination.limit, page=pagination.page
        )

    async def send_from_tc(
        self,
        session: AsyncSession,
        tc_transaction: TonConnectTransaction,
        user: User,
        reason: TransactionReason,
        metadata: FTMetadata,
    ) -> Transaction:
        transaction = await self._create_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=reason,
            metadata=metadata,
        )

        await session.refresh(user, with_for_update=True)

        # NOTE: in this case, ton transaction is unsaved here, which is good.
        if user.balance <= transaction.amount:
            raise InsuficcientFunds(required_amount=transaction.amount)

        user.balance -= transaction.amount

        log.info(
            "fragment_transaction.send_from_tc",
            fragment_transaction_id=transaction.id,
        )

        enqueue_task(
            fragment_transaction_process,
            transaction_id=transaction.id,
            tc_transaction=tc_transaction,
        )

        return transaction

    async def _create_from_tc(
        self,
        session: AsyncSession,
        tc_transaction: TonConnectTransaction,
        user: User,
        reason: TransactionReason,
        metadata: FTMetadata,
    ) -> Transaction:
        validate_tc_transaction(tc_transaction)
        tc_msg = tc_transaction.messages[0]
        transaction = await ton_transaction_service.create_as_tc(
            session=session, tc_transaction=tc_transaction
        )

        without_fee_f_amount = float(to_amount(tc_msg.amount))
        f_amount = after_fee(after_ton_network_fee(without_fee_f_amount))

        repository = TransactionRepository.from_session(session)

        return await repository.create(
            Transaction(
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

    async def get_chart_data(
        self, session: AsyncSession, user: User
    ) -> list[ChartPoint]:
        days_count = 90

        today = utc_now().date()
        start_date = today - timedelta(days=days_count - 1)

        stmt = (
            select(
                func.date(Transaction.created_at).label("date"),
                func.sum(
                    case(
                        (
                            Transaction.reason == "stars",
                            Transaction.amount,
                        ),
                        else_=0,
                    ).label("stars_spend")
                ),
                func.sum(
                    case(
                        (
                            Transaction.reason == "premium",
                            Transaction.amount,
                        ),
                        else_=0,
                    ).label("premium_spend")
                ),
            )
            .where(
                Transaction.user == user,
                Transaction.reason == TransactionReason.stars,
                # NOTE: might add `Transaction.created_at` to that lol
            )
            .group_by(func.date(Transaction.created_at))
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

            result.append(
                ChartPoint(
                    date=day,
                    stars_spend=row[1],
                    premium_spend=row[2],
                )
            )

        return result


transaction = TransactionService()
