from src.kit.schemas import Schema
from src.openapi import APITag
from src.routing import APIRouter

router = APIRouter(prefix="/ton", tags=["Ton", APITag.public])


class TonRate(Schema):
    ton_rate: float


@router.get("/rate")
async def get_ton_rate() -> TonRate:
    return TonRate(ton_rate=1.25)
