import structlog
from fastapi import Depends, Query
from pydantic import UUID4

from src.integrations.fragment import Fragment, get_fragment
from src.logging import Logger
from src.openapi import APITag, error_responses
from src.postgres import AsyncSession, get_db_session
from src.redis import Redis, get_redis
from src.routing import APIRouter
from src.schemas import TelegramUsername
from src.stars import auth
from src.stars.schemas import (
    BulkBuyStars,
    BulkBuyStarsResponse,
    BuyStars,
    BuyStarsResponse,
    StarsRecipient,
)
from src.stars.service import stars as stars_service
from src.stars.tasks import stars_bulk_purchase_process
from src.worker import enqueue_task

router = APIRouter(
    prefix="/stars",
    tags=["stars", APITag.public],
    responses=error_responses(401, 429),
)

log: Logger = structlog.get_logger()


@router.get(
    "/recipient/{username}",
    summary="Get Stars Recipient",
    description="Get stars recipient info",
    responses=error_responses(400, 404),
)
async def get_recipient(
    auth_subject: auth.StarsGlobal,
    username: TelegramUsername,
    fragment: Fragment = Depends(get_fragment),
    redis: Redis = Depends(get_redis),
    quantity: int | None = Query(
        default=None, description="Quantity of stars you are going to buy"
    ),
) -> StarsRecipient:
    log.debug(
        "Get recipient request from",
        user=auth_subject.subject,
        username=auth_subject.subject.username,
        recipient_username=username,
    )

    return await stars_service.get_recipient(
        fragment=fragment, username=username, redis=redis, quantity=quantity
    )


@router.post(
    "/buy",
    description="Buys stars for a given user.",
    responses=error_responses(400, 404),
)
async def buy_stars(
    auth_subject: auth.StarsGlobal,
    data: BuyStars,
    session: AsyncSession = Depends(get_db_session),
    fragment: Fragment = Depends(get_fragment),
    redis: Redis = Depends(get_redis),
) -> BuyStarsResponse:
    return await stars_service.buy(
        session=session,
        user=auth_subject.subject,
        data=data,
        fragment=fragment,
        redis=redis,
    )


@router.post(
    "/buy/bulk",
    status_code=202,
    description=(
        "Starts buying stars for many users at once. Returns right away; poll "
        "`GET /v1/stars/buy/bulk/{id}` for each item's result. Only items that are "
        "bought get charged, all sent in one wallet transaction."
    ),
)
async def bulk_buy_stars(
    auth_subject: auth.StarsGlobal,
    data: BulkBuyStars,
    session: AsyncSession = Depends(get_db_session),
) -> BulkBuyStarsResponse:
    bulk = await stars_service.create_bulk(
        session=session, user=auth_subject.subject, data=data
    )
    enqueue_task(stars_bulk_purchase_process, bulk_purchase_id=bulk.id)
    return stars_service.bulk_response(bulk)


@router.get(
    "/buy/bulk/{id}",
    description="Get a stars bulk purchase and its results",
    responses=error_responses(404),
)
async def get_bulk_buy_stars(
    auth_subject: auth.StarsGlobal,
    id: UUID4,
    session: AsyncSession = Depends(get_db_session),
) -> BulkBuyStarsResponse:
    bulk = await stars_service.get_bulk(
        session=session, user=auth_subject.subject, id=id
    )
    return stars_service.bulk_response(bulk)
