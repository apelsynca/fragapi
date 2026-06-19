from fastapi import Depends, Query

from src.auth.dependencies import AuthorizeWebUser
from src.deposit import sorting
from src.deposit.schemas import Deposit, DepositTonRequestMessage
from src.deposit.service import deposit as deposit_service
from src.kit.pagination import ListResource, PaginationParamsQuery
from src.postgres import AsyncSession, get_db_session
from src.routing import APIRouter

router = APIRouter(prefix="/deposits")


@router.post("/ton", description="Request a new ton deposit")
async def request_ton_deposit(
    auth_subject: AuthorizeWebUser,
    amount: float = Query(...),
    session: AsyncSession = Depends(get_db_session),
) -> DepositTonRequestMessage:
    return await deposit_service.create_ton(
        session=session, user=auth_subject.subject, amount=amount
    )


@router.get("/", description="List deposits")
async def get_list(
    auth_subject: AuthorizeWebUser,
    pagination: PaginationParamsQuery,
    sorting: sorting.ListSorting,
    session: AsyncSession = Depends(get_db_session),
) -> ListResource[Deposit]:
    deposits, count = await deposit_service.fetch_list(
        session=session,
        user=auth_subject.subject,
        sorting=sorting,
        pagination=pagination,
    )

    return ListResource.from_paginated_results(
        items=[Deposit.model_validate(deposit) for deposit in deposits],
        pagination_params=pagination,
        total_count=count,
    )
