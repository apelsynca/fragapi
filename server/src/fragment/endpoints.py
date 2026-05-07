from fastapi import Depends

from src.auth.dependencies import AuthorizeWebUser
from src.fragment.schemas import TonRate
from src.fragment_rest import get_fragment_rest
from src.fragment_rest.rest import FragmentRest
from src.openapi import APITag
from src.routing import APIRouter

router = APIRouter(prefix="/panel/fragment", tags=[APITag.private])


@router.get("/rate")
async def get_ton_rate(
    auth_subject: AuthorizeWebUser,
    fragment_rest: FragmentRest = Depends(get_fragment_rest),
) -> TonRate:
    ton_rate = await fragment_rest.get_ton_rate()
    return TonRate(ton_rate=ton_rate)
