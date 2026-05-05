from src.auth.dependencies import AuthorizeWebUser
from src.logging import get_logger
from src.openapi import APITag
from src.routing import APIRouter

router = APIRouter(
    prefix="/panel/transactions", tags=["Transactions", "Panel", APITag.private]
)

log = get_logger()


@router.get("/stats")
async def get_transaction_stats(user: AuthorizeWebUser):
    pass
