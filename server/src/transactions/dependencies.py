from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres import get_db_session

from .repository import TransactionRepository
from .service import TransactionService


def get_transaction_service(
    session: AsyncSession = Depends(get_db_session),
) -> TransactionService:
    return TransactionService(TransactionRepository(session=session))


TransactionServiceDependency = Annotated[
    TransactionService, Depends(get_transaction_service)
]
