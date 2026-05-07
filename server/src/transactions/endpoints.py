from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import AuthorizeWebUser
from src.kit.pagination import ListResource, PaginationParamsQuery
from src.logging import get_logger
from src.openapi import APITag
from src.postgres import get_db_session
from src.routing import APIRouter
from src.transactions import auth
from src.transactions.schemas import Transaction as TransactionSchema
from src.transactions.service import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions", APITag.public])

log = get_logger()


# change auth subject to diff
@router.get("/", description="List transactions")
async def list(
    auth_subject: auth.TransactionsRead,
    pagination: PaginationParamsQuery,
    session: AsyncSession = Depends(get_db_session),
) -> ListResource[TransactionSchema]:
    transactions, count = await transaction_service.paginate(
        session=session, pagination=pagination, user=auth_subject.subject
    )

    return ListResource.from_paginated_results(
        items=[
            TransactionSchema.model_validate(transaction)
            for transaction in transactions
        ],
        total_count=count,
        pagination_params=pagination,
    )


@router.get("/stats")
async def get_transaction_stats(user: AuthorizeWebUser):
    pass
