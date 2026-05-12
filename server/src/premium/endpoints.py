from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.fragment import Fragment, get_fragment
from src.logging import get_logger
from src.openapi import APITag
from src.postgres import get_db_session
from src.premium import auth
from src.premium.schemas import BuyPremium, BuyPremiumResponse, PremiumRecipient
from src.premium.service import premium as premium_service
from src.routing import APIRouter
from src.wallet.dependencies import get_wallet_manager
from src.wallet.manager import WalletManager

router = APIRouter(prefix="/premium", tags=["Premium", APITag.public])

log = get_logger()


@router.post("/buy", description="Buy premium subscription for a user.")
async def buy_premium(
    auth_subject: auth.PremiumGlobal,
    data: BuyPremium,
    session: AsyncSession = Depends(get_db_session),
    fragment: Fragment = Depends(get_fragment),
    wallet_manager: WalletManager = Depends(get_wallet_manager),
) -> BuyPremiumResponse:
    return await premium_service.buy(
        session=session,
        user=auth_subject.subject,
        data=data,
        fragment=fragment,
        wallet_manager=wallet_manager,
    )


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
