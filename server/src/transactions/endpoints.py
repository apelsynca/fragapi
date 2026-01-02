from src.auth.dependencies import WebUser
from src.exceptions import ResourceNotFound
from src.kit.pagination import ListResource, PaginationParamsQuery
from src.logging import get_logger
from src.models import TransactionStatus
from src.openapi import APITag
from src.routing import APIRouter
from src.ton_wallet import tonapi_client

from .dependencies import TransactionServiceDependency
from .schemas import Transaction, TransactionStats, TransactionVerifyResponse

router = APIRouter(
    prefix="/panel/transactions", tags=["Transactions", "Panel", APITag.private]
)

log = get_logger()


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


@router.post("/{transaction_id}/verify", description="Verify transaction status on blockchain")
async def verify_transaction(
    transaction_id: int,
    user: WebUser,
    transaction_service: TransactionServiceDependency,
) -> TransactionVerifyResponse:
    """
    Verify transaction status by checking blockchain.
    Returns verification result with updated status.
    """
    transaction = await transaction_service.get_by_id(transaction_id, user)

    if not transaction:
        raise ResourceNotFound("Transaction not found")

    # If no tx_hash, we can't verify on blockchain
    if not transaction.tx_hash:
        return TransactionVerifyResponse(
            id=transaction.id,
            status=transaction.status,
            tx_hash=None,
            verified=False,
            message="Транзакция не имеет хеша блокчейна для проверки",
        )

    try:
        # Try to get transaction from TON blockchain
        blockchain_tx = await tonapi_client.get_transaction(transaction.tx_hash)

        # Transaction exists on blockchain - it's completed
        if transaction.status != TransactionStatus.COMPLETED:
            await transaction_service.update_status(
                transaction=transaction,
                status=TransactionStatus.COMPLETED,
            )

        log.info(
            "Transaction verified on blockchain",
            transaction_id=transaction.id,
            tx_hash=transaction.tx_hash,
        )

        return TransactionVerifyResponse(
            id=transaction.id,
            status=TransactionStatus.COMPLETED,
            tx_hash=transaction.tx_hash,
            verified=True,
            message="Транзакция подтверждена в блокчейне",
        )

    except Exception as exc:
        log.warning(
            "Failed to verify transaction on blockchain",
            transaction_id=transaction.id,
            tx_hash=transaction.tx_hash,
            error=str(exc),
        )

        return TransactionVerifyResponse(
            id=transaction.id,
            status=transaction.status,
            tx_hash=transaction.tx_hash,
            verified=False,
            message=f"Не удалось проверить транзакцию: {str(exc)}",
        )
