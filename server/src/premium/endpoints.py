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


# async def buy_premium(
#     user: AuthorizeAPIUser,
#     data: BuyPremium,
# ) -> BuyPremiumResponse:
#     tx_hash = await premium_service.buy(
#         user=user.subject,
#         username=data.username,
#         months=data.months,
#     )
#
#     return BuyPremiumResponse(success=True, transaction_hash=tx_hash)
#
@router.get("/recipient/{username}", description="Get premium recipient")
async def get_recipient(
    username: str, auth_subject: AuthorizeAPIUser
) -> PremiumRecipient:
    raise


#     log.info("Search premium recipient request", user_id=auth_subject.subject.id)
#
#     return await premium_service.get_recipient(username=username)
