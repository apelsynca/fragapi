from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.fragment_transaction import auth, sorting
from src.fragment_transaction.schemas import (
    ChartPoint,
    FragmentTransaction,
    FragmentTransactionsStats,
)
from src.fragment_transaction.service import (
    fragment_transaction as fragment_transaction_service,
)
from src.kit.pagination import ListResource, PaginationParamsQuery
from src.kit.routing import APITag
from src.postgres import get_db_session
from src.routing import APIRouter

router = APIRouter(prefix="/transactions", tags=["", APITag.public])


@router.get("", description="Fragment transactions list")
async def list_transactions(
    auth_subject: auth.TransactionsRead,
    pagination: PaginationParamsQuery,
    sorting: sorting.ListSorting,
    session: AsyncSession = Depends(get_db_session),
) -> ListResource[FragmentTransaction]:
    transactions, count = await fragment_transaction_service.fetch_list(
        session=session,
        user=auth_subject.subject,
        sorting=sorting,
        pagination=pagination,
    )

    return ListResource.from_paginated_results(
        items=[FragmentTransaction.model_validate(t) for t in transactions],
        total_count=count,
        pagination_params=pagination,
    )


@router.get("/stats", description="Fragment transactions stats")
async def get_transactions_stats(
    auth_subject: auth.TransactionsRead,
    session: AsyncSession = Depends(get_db_session),
) -> FragmentTransactionsStats:
    return await fragment_transaction_service.get_stats(
        session=session, user=auth_subject.subject
    )


@router.get("/chart", description="Get fragment transactions chart data")
async def get_chart_data(
    auth_subject: auth.TransactionsRead, session: AsyncSession = Depends(get_db_session)
) -> list[ChartPoint]:
    return await fragment_transaction_service.get_chart_data(
        session=session, user=auth_subject.subject
    )
