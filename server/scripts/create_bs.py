import asyncio
import random
from secrets import token_urlsafe

from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_nano

from src.fragment_transaction.repository import FragmentTransactionRepository
from src.kit.database.postgres import create_async_sessionmaker
from src.models import FragmentTransaction, Transaction
from src.models.fragment_transactions import FragmentTransactionReason
from src.postgres import create_async_engine
from src.user.repository import UserRepository


async def main() -> None:
    engine = create_async_engine("script")
    sessionmaker = create_async_sessionmaker(engine)

    async with sessionmaker() as session:
        await create_trans(session)


async def create_trans(session: AsyncSession):
    user_repository = UserRepository.from_session(session)
    user = await user_repository.get_by_id(id=99999)
    if user is None:
        print("Exit, user with id 99999 none")
        return

    repository = FragmentTransactionRepository.from_session(session)

    while True:
        ipt = input("Amount:")
        if ipt == "":
            break
        amount = float(ipt)

        r = random.randint(1, 6)

        stars_amount = None
        premium_months = None

        if r == 1:
            reason = FragmentTransactionReason.premium
            premium_months = 3
        else:
            stars_amount = random.randint(25, 500)
            reason = FragmentTransactionReason.stars

        transaction = Transaction(
            nano_amount=to_nano(amount),
            message_hash="faketransa" + token_urlsafe(10),
            from_address="bbbbbR8wYxL4mZ2pT7vN1cQ9jS3dX8zV5fW6qB4nL0tM1rP",
            to_address="bbbbbR8wYxL4mZ2pT7vN1cQ9jS3dX8zV5fW6qB4nL0tM1rP",
        )
        transa = await repository.create(
            FragmentTransaction(
                user=user,
                amount=amount,
                reason=reason,
                recipient="Anyone",
                recipient_username="someoneelse",
                transaction=transaction,
                stars_amount=stars_amount,
                premium_months=premium_months,
            ),
            flush=True,
        )
        print(f"Created {transa.amount} TON - {transa.reason} for 99999")

    await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
