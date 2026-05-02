from src.auth.dependencies import AuthorizeWebUser
from src.kit.pagination import ListResource, PaginationParamsQuery
from src.logging import get_logger
from src.openapi import APITag
from src.routing import APIRouter
from src.transactions.schemas import Transaction, TransactionStats

router = APIRouter(
    prefix="/panel/transactions", tags=["Transactions", "Panel", APITag.private]
)

log = get_logger()


@router.get("", description="List all transactions")
async def get_transactions_list(
    auth_subject: AuthorizeWebUser,
    pagination: PaginationParamsQuery,
) -> ListResource[Transaction]:
    transactions, count = await transaction_service.get_list(
        pagination=pagination, user=auth_subject.subject
    )

    return ListResource.from_paginated_results(
        items=[Transaction.model_validate(transaction) for transaction in transactions],
        total_count=count,
        pagination_params=pagination,
    )


@router.get("/stats", description="Get transaction statistics")
async def get_transaction_stats(
    auth_subject: AuthorizeWebUser,
) -> TransactionStats:
    return await transaction_service.get_stats(auth_subject.subject)
