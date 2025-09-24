from src.auth.endpoints import router as auth_router
from src.premium.endpoints import router as premium_router
from src.routing import APIRouter
from src.stars.endpoints import router as stars_router
from src.transactions.endpoints import router as transactions_router
from src.users.endpoints import (
    panel_router as users_panel_router,
)
from src.users.endpoints import (
    router as users_router,
)

router = APIRouter(prefix="/v1")

router.include_router(users_router)
router.include_router(users_panel_router)
router.include_router(auth_router)
router.include_router(stars_router)
router.include_router(premium_router)
router.include_router(transactions_router)
