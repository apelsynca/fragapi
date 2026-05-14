import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.payment.repository import PaymentRepository
from src.payment.service import payment as payment_service


@pytest.mark.asyncio
async def test_creates_right(session: AsyncSession, user: User) -> None:
    payment = await payment_service.create(session=session, user=user, amount=0.123)

    repository = PaymentRepository.from_session(session)
    found_pay = await repository.get_by_id(id=payment.id)

    assert found_pay is not None
    assert found_pay.user == user


# Not to
# @pytest.mark.asyncio
# async def test_also_accepts_transaction(
#     session: AsyncSession, user: User, transaction: Transaction
# ) -> None:
#     payment = await payment_service.create(
#         session=session, user=user, amount=52.25, transaction=transaction
#     )
#
#     repository = PaymentRepository.from_session(session)
#     found_pay = await repository.get_by_id(id=payment.id)
#
#     assert found_pay is not None
#     assert found_pay.transaction == transaction
