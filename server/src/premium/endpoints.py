from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.integrations.fragment import Fragment, get_fragment
from src.logging import get_logger
from src.openapi import APITag
from src.postgres import get_db_session
from src.premium import auth
from src.premium.schemas import BuyPremium, BuyPremiumResponse, PremiumRecipient
from src.premium.service import premium as premium_service
from src.routing import APIRouter

router = APIRouter(prefix="/premium", tags=["premium", APITag.public])

log = get_logger()


@router.get("/recipient/{username}", description="Get premium recipient")
async def get_recipient(
    auth_subject: auth.PremiumGlobal,
    username: str,
    fragment: Fragment = Depends(get_fragment),
) -> PremiumRecipient:
    log.info(
        "Get recipient request from",
        user=auth_subject.subject,
        username=auth_subject.subject.username,
        recipient_username=username,
    )

    return await premium_service.get_recipient(fragment=fragment, username=username)


@router.post("/buy", description="Buy premium subscription for a user.")
async def buy_premium(
    auth_subject: auth.PremiumGlobal,
    data: BuyPremium,
    session: AsyncSession = Depends(get_db_session),
    fragment: Fragment = Depends(get_fragment),
) -> BuyPremiumResponse:
    return await premium_service.buy(
        session=session,
        user=auth_subject.subject,
        data=data,
        fragment=fragment,
    )
