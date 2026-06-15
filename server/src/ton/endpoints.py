from fastapi import Depends

from src.auth.dependencies import Authenticator
from src.auth.scope import Scope
from src.integrations.fragment import Fragment, get_fragment
from src.kit.schemas import Schema
from src.models import User
from src.openapi import APITag
from src.routing import APIRouter

router = APIRouter(
    prefix="/ton",
    tags=["ton", APITag.private],
    dependencies=[
        Depends(
            Authenticator(
                required_scopes={Scope.ton_rate_read}, allowed_subjects={User}
            )
        )
    ],
)


class TonRate(Schema):
    ton_rate: float


@router.get("/rate")
async def get_ton_rate(fragment: Fragment = Depends(get_fragment)) -> TonRate:
    ton_rate = await fragment.get_ton_usd_rate()
    return TonRate(ton_rate=ton_rate)
