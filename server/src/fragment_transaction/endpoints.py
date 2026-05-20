from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.fragment_transaction import auth
from src.fragment_transaction.schemas import FragmentTransactionsStats
from src.fragment_transaction.service import (
    fragment_transaction as fragment_transaction_service,
)
from src.kit.routing import APITag
from src.postgres import get_db_session
from src.routing import APIRouter

router = APIRouter(prefix="/transactions", tags=["", APITag.public])


@router.get("/stats")
async def get_transactions_stats(
    auth_subject: auth.TransactionsRead,
    session: AsyncSession = Depends(get_db_session),
) -> FragmentTransactionsStats:
    return await fragment_transaction_service.get_stats(
        session=session, user=auth_subject.subject
    )
