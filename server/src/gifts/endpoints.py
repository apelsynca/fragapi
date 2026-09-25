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
    description="List gift model short names by collection short_name",
)
async def get_gift_models_short_names(short_name: str) -> list[str]:
    return await gift_service.get_all_gift_model_strings_by_shortname(
        short_name=short_name
    )


@router.get("/{short_name}/models", description="Get collection giftmodels")
async def get_gift_models_by_collection(
    short_name: str, sorting: sorting.ListSorting
) -> list[GiftModel]:
    data = await thermos_service.get_collection_models(short_name)

    # TODO: yeah i know its shit, redo later ofc.
    if len(sorting) > 1:
        data = sorted(data, key=lambda p: p.floor, reverse=sorting[0][1])

    return data


@router.get(
    "/{short_name}/models/{name}", description="Get gift model by collection and name"
)
async def get_gift_model_by_collection_and_name(
    short_name: str,
    name: str,
) -> GiftModel:
    return await thermos_service.find_collection_model(
        short_name=short_name, model=name
    )
