import random
import string

import pytest_asyncio

from src.kit.jwt import encode_token
from src.kit.utils import generate_api_key
from src.models import User, UserSession
from tests.fixtures.database import SaveFixture


def rstr(prefix: str) -> str:
    return prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def lstr(suffix: str) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6)) + suffix


@pytest_asyncio.fixture
async def user(save_fixture: SaveFixture) -> User:
    return await create_user(save_fixture)


async def create_user(save_fixture: SaveFixture) -> User:
    user = User(first_name=rstr("Mock"), username=rstr("test_"))
    await save_fixture(user)
    return user


@pytest_asyncio.fixture
async def user_session(save_fixture: SaveFixture, user: User) -> UserSession:
    user_session = UserSession(
        token=encode_token(user.id, user.first_name),
        bot_hash=generate_api_key(),
        user=user,
    )
    await save_fixture(user_session)
    return user_session
