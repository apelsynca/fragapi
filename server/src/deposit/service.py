from collections.abc import Sequence
from secrets import token_urlsafe

import structlog
from sqlalchemy.orm import selectinload
from ton_core import to_amount, to_nano

from src.backoffice.telegram_logs.deposits import enqueue_new_deposit_admin_log_task
from src.config import settings
from src.deposit.repository import DepositRepository
from src.deposit.schemas import DepositTonRequestMessage
from src.deposit.sorting import DepositSortProperty
from src.deposit.ton_payload import TonDepositPayload
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.kit.pagination import PaginationParams
from src.kit.sorting import Sorting
from src.logging import Logger
from src.models import Deposit, TonTransaction, User
from src.models.deposits import DepositStatus
from src.postgres import AsyncSession

log: Logger = structlog.get_logger()


class DepositService:
    async def fetch_list(
        self,
        session: AsyncSession,
        user: User,
        pagination: PaginationParams,
        sorting: list[Sorting[DepositSortProperty]] = [
            (DepositSortProperty.created_at, True)
        ],
    ) -> tuple[Sequence[Deposit], int]:
        repository = DepositRepository.from_session(session)

        stmt = (
            repository.get_base_stmt()
            .where(Deposit.user == user, Deposit.status == DepositStatus.completed)
            .options(selectinload(Deposit.ton_transaction))
        )
        stmt = repository.apply_sorting(stmt=stmt, sorting=sorting)

        return await repository.paginate(
            stmt=stmt, limit=pagination.limit, page=pagination.page
        )

    async def create_ton(
        self, session: AsyncSession, user: User, amount: float
    ) -> DepositTonRequestMessage:
        deposit = await self.create(session=session, user=user, amount=amount)

        return DepositTonRequestMessage(
            address=settings.TON_ADDRESS,
            amount=str(to_nano(deposit.amount)),
            payload=TonDepositPayload(hash=deposit.hash).get_base64(),
        )

    async def create(
        self,
        session: AsyncSession,
        user: User,
        amount: float,
    ) -> Deposit:
        if amount < settings.MIN_TON_DEPOSIT_AMOUNT:
            raise BadRequest(
                f"Minimal deposit amount is {settings.MIN_TON_DEPOSIT_AMOUNT}"
            )

        repository = DepositRepository.from_session(session)
        deposit = await repository.create(
            Deposit(user=user, amount=amount, hash=token_urlsafe(14)), flush=True
        )

        log.info(
            "deposit.created",
            amount=deposit.amount,
            hash=deposit.hash,
            user_id=deposit.user_id,
        )

        return deposit

    async def complete_ton(
        self, session: AsyncSession, transaction: TonTransaction, ref_hash: str
    ) -> None:
        repository = DepositRepository.from_session(session)
        deposit = await repository.get_by_hash(hash=ref_hash)

        if deposit is None:
            raise ResourceNotFound("Deposit not found")

        if deposit.status == DepositStatus.completed:
            raise FragError("Status is wrong")

        if deposit.ton_transaction is not None:
            raise FragError("Deposit already has transaction")

        transaction_amount = float(to_amount(transaction.nano_amount))
        if deposit.amount != transaction_amount:
            raise BadRequest("Deposit amount and transaction amount is different")

        deposit.ton_transaction = transaction
        deposit.status = DepositStatus.completed

        deposit.user.balance += transaction_amount

        log.info(
            "deposit.completed",
            user_id=deposit.user_id,
            hash=deposit.hash,
            transaction_amount=transaction_amount,
        )

        enqueue_new_deposit_admin_log_task(deposit=deposit)


deposit = DepositService()
