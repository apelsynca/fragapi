from fastapi import Depends

from src.auth.dependencies import ApiUserAuthenticator
from src.gifts.service import gift as gift_service
from src.routing import APIRouter
from src.thermos.schemas import GiftModel
from src.thermos.service import thermos as thermos_service

router = APIRouter(prefix="/gifts", dependencies=[Depends(ApiUserAuthenticator)])


@router.get(
    "/{short_name}/short-models",
    description="List gift models short names by short_name",
)
async def get_gift_models_short_names(short_name: str) -> list[str]:
    return await gift_service.get_models_by_shortname(short_name)


@router.get("/{short_name}/models", description="Get gift collection models")
async def get_collection_models(short_name: str) -> list[GiftModel]:
    return await thermos_service.get_collection_models(short_name)


@router.get("/{short_name}/models/{name}", description="Get gift collection model")
async def get_model(
    short_name: str,
    name: str,
) -> GiftModel:
    return await thermos_service.find_collection_model(
        short_name=short_name, model=name
    )
