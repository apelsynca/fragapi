from fastapi import Depends

from src.kit.pagination import ListResource, PaginationParamsQuery
from src.kit.routing import APITag
from src.postgres import AsyncSession, get_db_session
from src.routing import APIRouter
from src.transaction import auth, sorting
from src.transaction.schemas import ChartPoint, Transaction, TransactionStats
from src.transaction.service import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions", APITag.public])


@router.get("", description="Fragment transactions list")
async def list_transactions(
    auth_subject: auth.TransactionsRead,
    pagination: PaginationParamsQuery,
    sorting: sorting.ListSorting,
    session: AsyncSession = Depends(get_db_session),
) -> ListResource[Transaction]:
    transactions, count = await transaction_service.fetch_list(
        session=session,
        user=auth_subject.subject,
        sorting=sorting,
        pagination=pagination,
    )

    return ListResource.from_paginated_results(
        items=[Transaction.model_validate(t) for t in transactions],
        total_count=count,
        pagination_params=pagination,
    )


@router.get("/stats", description="Fragment transactions stats", tags=[APITag.private])
async def get_transactions_stats(
    auth_subject: auth.TransactionsRead,
    session: AsyncSession = Depends(get_db_session),
) -> TransactionStats:
    return await transaction_service.get_stats(
        session=session, user=auth_subject.subject
    )


@router.get(
    "/chart", description="Get fragment transactions chart data", tags=[APITag.private]
)
async def get_chart_data(
    auth_subject: auth.TransactionsRead, session: AsyncSession = Depends(get_db_session)
) -> list[ChartPoint]:
    return await transaction_service.get_chart_data(
        session=session, user=auth_subject.subject
    )
