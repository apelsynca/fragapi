from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import AuthorizeWebUser
from src.kit.ton_connect import TonConnectMessage
from src.payments.service import payment as payment_service
from src.postgres import get_db_session
from src.routing import APIRouter

router = APIRouter(prefix="/payments")


@router.get("/ton")
async def request_ton_payment(
    auth_subject: AuthorizeWebUser,
    amount: float = Query(...),
    session: AsyncSession = Depends(get_db_session),
) -> TonConnectMessage:
    return await payment_service.ton_payment_request(
        session=session, user=auth_subject.subject, amount=amount
    )
