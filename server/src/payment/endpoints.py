from decimal import Decimal

from fastapi import Depends, Query

from src.auth.dependencies import AuthorizeWebUser
from src.kit.pagination import ListResource, PaginationParamsQuery
from src.payment import sorting
from src.payment.schemas import Payment, PaymentTonRequestMessage
from src.payment.service import payment as payment_service
from src.postgres import AsyncSession, get_db_session
from src.routing import APIRouter

router = APIRouter(prefix="/payments")


@router.post("/ton", description="Request a new ton payment")
async def request_ton_payment(
    auth_subject: AuthorizeWebUser,
    amount: Decimal = Query(...),
    session: AsyncSession = Depends(get_db_session),
) -> PaymentTonRequestMessage:
    return await payment_service.create_ton(
        session=session, user=auth_subject.subject, amount=amount
    )


@router.get("/", description="List payments")
async def get_list(
    auth_subject: AuthorizeWebUser,
    pagination: PaginationParamsQuery,
    sorting: sorting.ListSorting,
    session: AsyncSession = Depends(get_db_session),
) -> ListResource[Payment]:
    payments, count = await payment_service.fetch_list(
        session=session,
        user=auth_subject.subject,
        sorting=sorting,
        pagination=pagination,
    )

    return ListResource.from_paginated_results(
        items=[Payment.model_validate(payment) for payment in payments],
        pagination_params=pagination,
        total_count=count,
    )
