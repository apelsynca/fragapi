from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import AuthorizeAPIUser
from src.fragment_rest import get_fragment_rest
from src.fragment_rest.rest import FragmentRest
from src.openapi import APITag
from src.postgres import get_db_session
from src.premium.schemas import BuyPremium, BuyPremiumResponse, PremiumRecipient
from src.premium.service import premium as premium_service
from src.routing import APIRouter
from src.wallet.dependencies import get_wallet_manager
from src.wallet.manager import WalletManager

router = APIRouter(prefix="/premium", tags=["Premium", APITag.documented])


@router.post("/buy", description="Buy premium subscription for a user.")
async def buy_premium(
    auth_subject: AuthorizeAPIUser,
    data: BuyPremium,
    session: AsyncSession = Depends(get_db_session),
    fragment_rest: FragmentRest = Depends(get_fragment_rest),
    wallet_manager: WalletManager = Depends(get_wallet_manager),
) -> BuyPremiumResponse:
    transaction = await premium_service.get_buy_tc_transaction(
        fragment_rest=fragment_rest, username=data.username, months=data.months
    )

    return await premium_service.gift_from_tc_transaction(
        session=session,
        user=auth_subject.subject,
        wallet_manager=wallet_manager,
        transaction=transaction,
    )


@router.get("/recipient/{username}", description="Get premium recipient")
async def get_recipient(
    username: str, auth_subject: AuthorizeAPIUser
) -> PremiumRecipient:
    raise
