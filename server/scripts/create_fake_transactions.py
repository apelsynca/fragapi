import asyncio
from datetime import timedelta
from secrets import token_urlsafe

from sqlalchemy.ext.asyncio import AsyncSession

from src.kit.database.postgres import create_async_sessionmaker
from src.kit.utils import utc_now
from src.models.transactions import Transaction, TransactionReason, TransactionStatus
from src.models.user_sessions import UserSession
from src.postgres import create_async_engine
from src.transactions.repository import TransactionRepository
from src.users.repository import UserRepository


async def main() -> None:
    engine = create_async_engine("script")
    sessionmaker = create_async_sessionmaker(engine)

    async with sessionmaker() as session:
        await create_transactions(session)
        await session.commit()


async def create_transactions(session: AsyncSession) -> UserSession | None:
    repository = UserRepository.from_session(session)
    user = await repository.get_by_id(id=7433065810)

    if user is None:
        print("No user")
        return

    t_repository = TransactionRepository.from_session(session)

    while True:
        offset = input("Days offset (any key to stop): ")
        try:
            offset = int(offset)
        except Exception:
            return

        transaction = await t_repository.create(
            Transaction(
                amount=float(input(f"Amount for [{offset}]: ")),
                user=user,
                reason=TransactionReason.stars,
                recipient=token_urlsafe(24),
                message_hash=None,
                status=TransactionStatus.completed,
                created_at=utc_now() - timedelta(days=offset),
            )
        )

        print("Created transaction", transaction.amount, transaction.created_at)


if __name__ == "__main__":
    asyncio.run(main())
