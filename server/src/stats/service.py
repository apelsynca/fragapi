from datetime import timedelta

import structlog
from sqlalchemy import case, func, select

from src.enums import TransactionReason
from src.logging import Logger
from src.models import Transaction
from src.postgres import AsyncSession
from src.redis import Redis
from src.stats.schemas import StatsTotals

log: Logger = structlog.get_logger()

TOTALS_CACHE_KEY = "stats:totals"
TOTALS_CACHE_TIME = timedelta(minutes=1)


class StatsService:
    async def get_totals(self, session: AsyncSession, redis: Redis) -> StatsTotals:
        """
        Service-wide totals of what was bought, cached because the query scans
        every transaction.
        """
        cached = await self._get_cached_totals(redis)
        if cached is not None:
            return cached

        totals = await self._query_totals(session)
        await self._cache_totals(redis, totals)

        return totals

    async def _query_totals(self, session: AsyncSession) -> StatsTotals:
        # Transactions have no status: a failed send leaves its row without sent_at.
        statement = select(
            func.coalesce(
                func.sum(
                    case(
                        (
                            Transaction.reason == TransactionReason.stars,
                            Transaction.stars_amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("stars_total"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            Transaction.reason == TransactionReason.premium,
                            Transaction.premium_months,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("premium_months_total"),
        ).where(Transaction.sent_at.is_not(None))

        row = (await session.execute(statement)).one()

        return StatsTotals(
            stars_total=int(row.stars_total),
            premium_months_total=int(row.premium_months_total),
        )

    async def _get_cached_totals(self, redis: Redis) -> StatsTotals | None:
        try:
            redis_data = await redis.get(name=TOTALS_CACHE_KEY)
            if redis_data is None:
                return None

            return StatsTotals.model_validate_json(redis_data)
        except Exception:
            log.exception("Error getting the stats totals cache")
            return None

    async def _cache_totals(self, redis: Redis, totals: StatsTotals) -> None:
        try:
            await redis.set(
                name=TOTALS_CACHE_KEY,
                value=totals.model_dump_json(),
                ex=TOTALS_CACHE_TIME,
            )
        except Exception:
            log.exception("Error setting the stats totals cache")


stats = StatsService()
