from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import AuthorizeAPIUser
from src.fragment_rest import get_fragment_rest
from src.fragment_rest.rest import FragmentRest
from src.logging import get_logger
from src.openapi import APITag
from src.postgres import get_db_session
from src.routing import APIRouter
from src.stars.schemas import BuyStars, BuyStarsResponse, StarsRecipient
from src.stars.service import stars as stars_service

router = APIRouter(
    prefix="/stars",
    tags=["Stars", APITag.documented],
)

log = get_logger()


@router.post(
    "/buy", description="Buy stars for a user. Takes user username and stars quantity"
)
async def buy_stars(
    auth_subject: AuthorizeAPIUser,
    data: BuyStars,
    session: AsyncSession = Depends(get_db_session),
    fragment_rest: FragmentRest = Depends(get_fragment_rest),
) -> BuyStarsResponse:
    return await stars_service.buy(
        session=session,
        fragment_rest=fragment_rest,
        user_id=auth_subject.subject.id,
        quantity=data.quantity,
        username=data.username,
    )


@router.get("/recipient/{username}", description="Get stars recipient info")
async def get_recipient(
    auth_subject: AuthorizeAPIUser,
    username: str,
    fragment_rest: FragmentRest = Depends(get_fragment_rest),
) -> StarsRecipient:
    log.info(
        "Get recipient request from",
        user=auth_subject.subject,
        username=auth_subject.subject.username,
    )
    return await stars_service.get_recipient(
        fragment_rest=fragment_rest, username=username
    )
