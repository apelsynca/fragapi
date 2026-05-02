from src.auth.dependencies import AuthorizeAPIUser
from src.logging import get_logger
from src.openapi import APITag
from src.routing import APIRouter

from .schemas import (
    BuyPremium,
    BuyPremiumResponse,
    PremiumPriceResponse,
    PremiumRecipient,
)
from .service import premium_service

router = APIRouter(prefix="/premium", tags=["Premium", APITag.documented])

log = get_logger()


@router.post(
    "/buy",
    description="Buy premium subscription for a user. Takes user username and premium months",
)
async def buy_premium(
    user: AuthorizeAPIUser,
    data: BuyPremium,
) -> BuyPremiumResponse:
    tx_hash = await premium_service.buy(
        user=user.subject,
        username=data.username,
        months=data.months,
    )

    return BuyPremiumResponse(success=True, transaction_hash=tx_hash)


@router.get("/recipient/{username}", description="Get premium recipient")
async def get_recipient(
    username: str, auth_subject: AuthorizeAPIUser
) -> PremiumRecipient:
    log.info("Search premium recipient request", user_id=auth_subject.subject.id)

    return await premium_service.get_recipient(username=username)


@router.get("/price", description="Get premium prices")
async def get_price() -> PremiumPriceResponse:
    return PremiumPriceResponse(year=22.76, six_months=12.55, three_months=9.41)
