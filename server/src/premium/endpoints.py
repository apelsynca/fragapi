import structlog
from fastapi import Depends

from src.integrations.fragment import Fragment, get_fragment
from src.logging import Logger
from src.openapi import APITag, error_responses
from src.postgres import AsyncSession, get_db_session
from src.premium import auth
from src.premium.schemas import BuyPremium, BuyPremiumResponse, PremiumRecipient
from src.premium.service import premium as premium_service
from src.redis import Redis, get_redis
from src.routing import APIRouter
from src.schemas import TelegramUsername

router = APIRouter(
    prefix="/premium",
    tags=["premium", APITag.public],
    responses=error_responses(401, 429),
)

log: Logger = structlog.get_logger()


@router.get(
    "/recipient/{username}",
    summary="Get Premium Recipient",
    description="Get premium recipient",
    responses=error_responses(400, 404),
)
async def get_recipient(
    auth_subject: auth.PremiumGlobal,
    username: TelegramUsername,
    fragment: Fragment = Depends(get_fragment),
    redis: Redis = Depends(get_redis),
) -> PremiumRecipient:
    log.info(
        "Get recipient request from",
        user=auth_subject.subject,
        username=auth_subject.subject.username,
        recipient_username=username,
    )

    return await premium_service.get_recipient(
        fragment=fragment, username=username, redis=redis
    )


@router.post(
    "/buy",
    description="Buy premium subscription for a user.",
    responses=error_responses(400, 404),
)
async def buy_premium(
    auth_subject: auth.PremiumGlobal,
    data: BuyPremium,
    session: AsyncSession = Depends(get_db_session),
    fragment: Fragment = Depends(get_fragment),
    redis: Redis = Depends(get_redis),
) -> BuyPremiumResponse:
    return await premium_service.buy(
        session=session,
        user=auth_subject.subject,
        data=data,
        fragment=fragment,
        redis=redis,
    )
