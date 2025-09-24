from typing import Annotated

from fastapi import Depends

from src.database.dependencies import DBSession

from .repository import TransactionRepository
from .service import TransactionService


def get_transaction_service(session: DBSession) -> TransactionService:
    return TransactionService(TransactionRepository(session=session))


TransactionServiceDependency = Annotated[
    TransactionService, Depends(get_transaction_service)
]
