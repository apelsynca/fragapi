import base64
from secrets import token_urlsafe

from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import begin_cell, to_amount, to_nano

from src.config import settings
from src.consts import TON_COMMENT_TEMPLATE
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.models import Payment, Transaction, User
from src.models.payments import PaymentStatus
from src.payment.repository import PaymentRepository
from src.payment.schemas import PaymentTonRequestMessage
from src.payment.tasks import deposit_send_telegram_log
from src.worker import enqueue_task


class PaymentService:
    async def create_ton(
        self, session: AsyncSession, user: User, amount: float
    ) -> PaymentTonRequestMessage:
        payment = await self.create(session=session, user=user, amount=amount)

        payload_cell = (
            begin_cell()
            .store_uint(0, 32)
            .store_snake_string(TON_COMMENT_TEMPLATE.format(payment.hash))
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

        return await repository.create(payment, flush=True)

    async def complete_ton(
        self, session: AsyncSession, transaction: Transaction, hash: str
    ) -> None:
        repository = PaymentRepository.from_session(session)
        payment = await repository.get_by_hash(hash=hash)

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

        enqueue_task(deposit_send_telegram_log, payment_id=payment.id)


payment = PaymentService()
