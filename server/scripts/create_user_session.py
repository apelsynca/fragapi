import asyncio
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from src.kit.crypto import generate_token
from src.kit.database.postgres import create_async_sessionmaker
from src.models.user_sessions import USER_SESSION_PREFIX, UserSession
from src.postgres import create_async_engine
from src.users.repository import UserRepository


async def main() -> None:
    engine = create_async_engine("script")
    sessionmaker = create_async_sessionmaker(engine)

    async with sessionmaker() as session:
        user_session = await create_user_session(session)
        await session.commit()

        if user_session is None:
            print("Somehow user session is None idk why...")
            return

        print("Created user session")
        print("Bot hash:", user_session.bot_hash)
        print("Object", user_session)


async def create_user_session(session: AsyncSession) -> UserSession | None:
    repository = UserRepository.from_session(session)

    user_id_input = input("Enter user_id, or default [99999]: ")
    if not user_id_input:
        user_id = 99999
    else:
        user_id = int(user_id_input)

    user = await repository.get_by_id(id=user_id)

    if user is None:
        print("No user")
        return

    user_session = UserSession(
        user=user,
        user_agent=None,
        token=generate_token(prefix=USER_SESSION_PREFIX),
        bot_hash=secrets.token_urlsafe(24),
    )
    session.add(user_session)

    return user_session


if __name__ == "__main__":
    asyncio.run(main())
