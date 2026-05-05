from src.auth.dependencies import AuthorizeAPIUser
from src.openapi import APITag
from src.premium.schemas import BuyPremiumResponse, PremiumRecipient
from src.routing import APIRouter

router = APIRouter(prefix="/premium", tags=["Premium", APITag.documented])


@router.post(
    "/buy",
    description="Buy premium subscription for a user. Takes user username and premium months",
)
async def buy_premium() -> BuyPremiumResponse:
    raise


@router.get("/recipient/{username}", description="Get premium recipient")
async def get_recipient(
    username: str, auth_subject: AuthorizeAPIUser
) -> PremiumRecipient:
    raise
