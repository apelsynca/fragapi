from secrets import token_urlsafe

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragError, ResourceNotFound
from src.models import Payment, Transaction, User
from src.models.payments import PaymentStatus
from src.payment.repository import PaymentRepository


class PaymentService:
    async def create(
        self,
        session: AsyncSession,
        user: User,
        amount: float,
    ) -> Payment:
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
            raise FragError("Transaction is wrong")

        payment.transaction = transaction

        # here increase the users balance


payment = PaymentService()
