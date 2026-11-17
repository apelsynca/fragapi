from fastapi import Depends

from src.openapi import APITag
from src.postgres import AsyncSession, get_db_session
from src.redis import Redis, get_redis
from src.routing import APIRouter
from src.stats.schemas import StatsTotals
from src.stats.service import stats as stats_service

# Public on purpose: the landing page shows these totals to anonymous visitors.
router = APIRouter(prefix="/stats", tags=["stats", APITag.private])


@router.get("/totals", description="Stars and premium months bought via the service")
async def get_stats_totals(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> StatsTotals:
    return await stats_service.get_totals(session=session, redis=redis)
