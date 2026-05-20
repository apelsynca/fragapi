from src.auth.endpoints import router as auth_router
from src.fragment_transaction.endpoints import router as fragment_transactions_router
from src.gifts.endpoints import router as gifts_router
from src.payment.endpoints import router as payment_router
from src.premium.endpoints import router as premium_router
from src.routing import APIRouter
from src.stars.endpoints import router as stars_router
from src.ton.endpoints import router as ton_router
from src.tonapi.endpoints import router as tonapi_router
from src.users.endpoints import panel_router as users_panel_router
from src.users.endpoints import router as users_router

router = APIRouter(prefix="/v1")

router.include_router(users_router)
router.include_router(users_panel_router)
router.include_router(auth_router)
router.include_router(stars_router)
router.include_router(premium_router)
router.include_router(ton_router)
router.include_router(gifts_router)
router.include_router(tonapi_router)
router.include_router(payment_router)
router.include_router(fragment_transactions_router)
