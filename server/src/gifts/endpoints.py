from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.scope import Scope
from src.gifts import sorting
from src.gifts.service import gift as gift_service
from src.models import User
from src.openapi import APITag
from src.routing import APIRouter
from src.thermos.schemas import GiftModel
from src.thermos.service import thermos as thermos_service

router = APIRouter(
    prefix="/gifts",
    dependencies=[
        Depends(Authenticator(allowed_subjects={User}, required_scopes={Scope.api}))
    ],
    tags=["gifts", APITag.public],
)


@router.get(
    "/{short_name}/short-models",
    description="List gift models short names by short_name",
)
async def get_gift_models_short_names(short_name: str) -> list[str]:
    return await gift_service.get_models_by_shortname(short_name)


@router.get("/{short_name}/models", description="Get gift collection models")
async def get_collection_models(
    short_name: str, sorting: sorting.ListSorting
) -> list[GiftModel]:
    data = await thermos_service.get_collection_models(short_name)

    # yeah i know, redo later ofc.
    if len(sorting) > 1:
        data = sorted(data, key=lambda p: p.floor, reverse=sorting[0][1])

    return data


@router.get("/{short_name}/models/{name}", description="Get gift collection model")
async def get_model(
    short_name: str,
    name: str,
) -> GiftModel:
    return await thermos_service.find_collection_model(
        short_name=short_name, model=name
    )
