from src.auth.dependencies import WebUser
from src.kit.pagination import ListResource, PaginationParamsQuery
from src.openapi import APITag
from src.routing import APIRouter

from .dependencies import TransactionServiceDependency
from .schemas import Transaction, TransactionStats

router = APIRouter(
    prefix="/panel/transactions", tags=["Transactions", "Panel", APITag.private]
)


@router.get("", description="List all transactions")
async def get_transactions_list(
    user: WebUser,
    pagination: PaginationParamsQuery,
    transaction_service: TransactionServiceDependency,
) -> ListResource[Transaction]:
    transactions, count = await transaction_service.get_list(
        pagination=pagination, user=user
    )

    return ListResource.from_paginated_results(
        items=[Transaction.model_validate(transaction) for transaction in transactions],
        total_count=count,
        pagination_params=pagination,
    )


@router.get("/stats", description="Get transaction statistics")
async def get_transaction_stats(
    user: WebUser,
    transaction_service: TransactionServiceDependency,
) -> TransactionStats:
    return await transaction_service.get_stats(user)
