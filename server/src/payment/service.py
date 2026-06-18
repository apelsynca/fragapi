import base64
from collections.abc import Sequence
from secrets import token_urlsafe

import structlog
from ton_core import begin_cell, to_amount, to_nano

from src.backoffice.telegram_logs.deposits import enqueue_new_deposit_admin_log_task
from src.config import settings
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.kit.pagination import PaginationParams
from src.kit.sorting import Sorting
from src.logging import Logger
from src.models import Payment, Transaction, User
from src.models.payments import PaymentStatus
from src.payment.repository import PaymentRepository
from src.payment.schemas import PaymentTonRequestMessage
from src.payment.sorting import PaymentSortProperty
from src.postgres import AsyncSession

log: Logger = structlog.get_logger()


class PaymentService:
    TON_COMMENT_TEMPLATE = "FragAPI top-up\n\nRef#{}"

    async def fetch_list(
        self,
        session: AsyncSession,
        user: User,
        pagination: PaginationParams,
        sorting: list[Sorting[PaymentSortProperty]] = [
            (PaymentSortProperty.created_at, True)
        ],
    ) -> tuple[Sequence[Payment], int]:
        repository = PaymentRepository.from_session(session)

        stmt = repository.get_base_stmt().where(
            Payment.user == user, Payment.status == PaymentStatus.completed
        )
        stmt = repository.apply_sorting(stmt=stmt, sorting=sorting)

        return await repository.paginate(
            stmt=stmt, limit=pagination.limit, page=pagination.page
        )

    async def create_ton(
        self, session: AsyncSession, user: User, amount: float
    ) -> PaymentTonRequestMessage:
        payment = await self.create(session=session, user=user, amount=amount)

        payload_cell = (
            begin_cell()
            .store_uint(0, 32)
            .store_snake_string(self.TON_COMMENT_TEMPLATE.format(payment.hash))
            .end_cell()
        )
        payload_boc = payload_cell.to_boc()
        payload = base64.b64encode(payload_boc).decode("utf-8")

        return PaymentTonRequestMessage(
            address=settings.TON_ADDRESS,
            amount=str(to_nano(payment.amount)),
            payload=payload,
        )

    async def create(
        self,
        session: AsyncSession,
        user: User,
        amount: float,
    ) -> Payment:
        if amount < settings.MIN_TON_DEPOSIT_AMOUNT:
            raise BadRequest(
                f"Minimal deposit amount is {settings.MIN_TON_DEPOSIT_AMOUNT}"
            )

        repository = PaymentRepository.from_session(session)
        payment = Payment(user=user, amount=amount, hash=token_urlsafe(14))

        payment = await repository.create(payment, flush=True)

        log.info(
            "payment.created",
            amount=payment.amount,
            hash=payment.hash,
            user_id=payment.user_id,
        )

        return payment

    async def complete_ton(
        self, session: AsyncSession, transaction: Transaction, payment_hash: str
    ) -> None:
        repository = PaymentRepository.from_session(session)
        payment = await repository.get_by_hash(hash=payment_hash)

        if payment is None:
            raise ResourceNotFound("Payment not found")

        if payment.status == PaymentStatus.completed:
            raise FragError("Status is wrong")

        if payment.transaction is not None:
            raise FragError("Payment already has transaction")

        transaction_amount = float(to_amount(transaction.nano_amount))
        if payment.amount != transaction_amount:
            raise BadRequest("Payment amount and transaction amount is different")

        payment.transaction = transaction
        payment.status = PaymentStatus.completed

        payment.user.balance += transaction_amount

        log.info(
            "payment.completed",
            user_id=payment.user_id,
            hash=payment.hash,
            transaction_amount=transaction_amount,
        )

        enqueue_new_deposit_admin_log_task(payment=payment)


payment = PaymentService()
