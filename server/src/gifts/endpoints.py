from fastapi import Depends

from src.auth.dependencies import ApiUserAuthenticator
from src.gifts.service import gift as gift_service
from src.routing import APIRouter

router = APIRouter(prefix="/gifts", dependencies=[Depends(ApiUserAuthenticator)])


@router.get("/models/{short_name}", description="List gift models by short_name")
async def get_gift_models(short_name: str) -> list[str]:
    return await gift_service.get_models_by_shortname(short_name)
