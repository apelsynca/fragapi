from src.auth.dependencies import APIUser
from src.logging import get_logger
from src.openapi import APITag
from src.routing import APIRouter
from src.transactions.dependencies import TransactionServiceDependency
from src.users.dependencies import UserServiceDependency

from .schemas import BuyStars, BuyStarsResponse, StarsPriceResponse, StarsRecipient
from .service import stars_service

router = APIRouter(prefix="/stars", tags=["Stars", APITag.documented])

log = get_logger()


@router.post(
    "/buy", description="Buy stars for a user. Takes user username and stars quantity"
)
async def buy_stars(
    user: APIUser,
    data: BuyStars,
    user_service: UserServiceDependency,
    transaction_service: TransactionServiceDependency,
) -> BuyStarsResponse:
    tx_hash = await stars_service.buy(
        user_service=user_service,
        transaction_service=transaction_service,
        user=user,
        quantity=data.quantity,
        username=data.username,
    )

    return BuyStarsResponse(success=True, transaction_hash=tx_hash)


@router.get("/recipient/{username}", description="Get stars recipient")
async def get_recipient(username: str, user: APIUser) -> StarsRecipient:
    log.info("Search stars recipient request", user_id=user.id)

    return await stars_service.get_recipient(username=username)


@router.get("/price", description="Get price for a single star")
async def get_price() -> StarsPriceResponse:
    ton = await stars_service.get_price()

    return StarsPriceResponse(ton=ton)
