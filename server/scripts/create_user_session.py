import asyncio
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from src.kit.crypto import generate_token
from src.kit.database.postgres import create_async_sessionmaker
from src.kit.utils import generate_api_key
from src.models.user_sessions import USER_SESSION_PREFIX, UserSession
from src.models.users import User
from src.postgres import create_async_engine
from src.users.repository import UserRepository


async def main() -> None:
    engine = create_async_engine("script")
    sessionmaker = create_async_sessionmaker(engine)

    async with sessionmaker() as session:
        user_session = await create_user_session(session)
        await session.commit()
        print(user_session)


async def create_user_session(session: AsyncSession) -> UserSession | None:
    repository = UserRepository.from_session(session)

    await repository.create(
        User(
            id=99999,
            first_name="ME",
            username="fakehomocitrus",
            api_key=generate_api_key(),
        )
    )
    await session.commit()

    user = await repository.get_by_id(id=99999)

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
