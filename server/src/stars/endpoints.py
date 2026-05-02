from src.auth.dependencies import AuthorizeAPIUser
from src.openapi import APITag
from src.routing import APIRouter
from src.stars.schemas import (
    BuyStars,
    BuyStarsResponse,
    StarsPriceResponse,
    StarsRecipient,
)
from src.stars.service import stars as stars_service

router = APIRouter(prefix="/stars", tags=["Stars", APITag.documented])


@router.post(
    "/buy", description="Buy stars for a user. Takes user username and stars quantity"
)
async def buy_stars(
    auth_subject: AuthorizeAPIUser,
    data: BuyStars,
) -> BuyStarsResponse:
    tx_hash = await stars_service.buy(
        user=auth_subject.subject,
        quantity=data.quantity,
        username=data.username,
    )

    return BuyStarsResponse(success=True, transaction_hash=tx_hash)


@router.get("/recipient/{username}", description="Get stars recipient")
async def get_recipient(username: str) -> StarsRecipient:
    # log.info("Search stars recipient request", user_id=auth_subject.subject.id)

    return await stars_service.get_recipient(username=username)


@router.get("/price", description="Get price for a single star")
async def get_price() -> StarsPriceResponse:
    ton = await stars_service.get_price()

    return StarsPriceResponse(ton=ton)
