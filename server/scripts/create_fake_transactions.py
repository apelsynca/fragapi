import asyncio
import random
from datetime import timedelta
from secrets import token_urlsafe

from ton_core import to_nano

from src.fragment_transaction.repository import FragmentTransactionRepository
from src.kit.database.postgres import create_async_sessionmaker
from src.kit.utils import utc_now
from src.models import TonTransaction, UserSession
from src.models.fragment_transactions import (
    FragmentTransaction,
    FragmentTransactionReason,
)
from src.postgres import AsyncSession, create_async_engine
from src.ton_transaction.repository import TransactionRepository
from src.user.repository import UserRepository


async def main() -> None:
    engine = create_async_engine("script")
    sessionmaker = create_async_sessionmaker(engine)

    async with sessionmaker() as session:
        await create_transactions(session)
        await session.commit()


async def create_transactions(session: AsyncSession) -> UserSession | None:
    repository = UserRepository.from_session(session)
    user = await repository.get_by_id(id=99999)

    if user is None:
        print("No user")
        return

    usual_repo = TransactionRepository.from_session(session)

    while True:
        offset = input("Days offset (any key to stop): ")
        try:
            offset = int(offset)
        except Exception:
            return

        amount = float(input(f"Amount for [{offset}]: "))
        ton_transaction = await usual_repo.create(
            TonTransaction(
                nano_amount=to_nano(amount),
                hash="6ec1e3a7678ce211a44b5a98fbef46f299355a408978104941048e73f5db6cec",
                message_hash=None,
                created_at=utc_now() - timedelta(days=offset),
                from_address="from_fakeaddress",
                to_address="to_fakeaddress",
            )
        )

        frag_repo = FragmentTransactionRepository.from_session(session)
        frag_transaction = await frag_repo.create(
            FragmentTransaction(
                user=user,
                amount=amount,
                recipient=token_urlsafe(24),
                recipient_username="recipient_username_here",
                ton_transaction=ton_transaction,
                created_at=utc_now() - timedelta(days=offset),
                reason=FragmentTransactionReason.stars,
                stars_amount=[100, 125, 51, 200, 500][random.randint(1, 5)],
            )
        )

        print(
            "Created transaction + frag transaction",
            frag_transaction.amount,
            frag_transaction.created_at,
        )


if __name__ == "__main__":
    asyncio.run(main())
