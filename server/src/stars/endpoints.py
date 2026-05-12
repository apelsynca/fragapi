from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.fragment import Fragment, get_fragment
from src.logging import get_logger
from src.openapi import APITag
from src.postgres import get_db_session
from src.routing import APIRouter
from src.stars import auth
from src.stars.schemas import BuyStars, BuyStarsResponse, StarsRecipient
from src.stars.service import stars as stars_service
from src.wallet.dependencies import get_wallet_manager
from src.wallet.manager import WalletManager

router = APIRouter(
    prefix="/stars",
    tags=["Stars", APITag.public],
)

log = get_logger()


@router.post("/buy", description="Buys stars for a given user.")
async def buy_stars(
    auth_subject: auth.StarsGlobal,
    data: BuyStars,
    session: AsyncSession = Depends(get_db_session),
    fragment: Fragment = Depends(get_fragment),
    wallet_manager: WalletManager = Depends(get_wallet_manager),
) -> BuyStarsResponse:
    return await stars_service.buy(
        session=session,
        user=auth_subject.subject,
        data=data,
        fragment=fragment,
        wallet_manager=wallet_manager,
    )


@router.get("/recipient/{username}", description="Get stars recipient info")
async def get_recipient(
    auth_subject: auth.StarsGlobal,
    username: str,
    fragment: Fragment = Depends(get_fragment),
    quantity: int | None = Query(default=None),
) -> StarsRecipient:
    log.info(
        "Get recipient request from",
        user=auth_subject.subject,
        username=auth_subject.subject.username,
        recipient_username=username,
    )

    return await stars_service.get_recipient(
        fragment=fragment,
        username=username,
        quantity=quantity,
    )
