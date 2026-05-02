import random
import string

import pytest_asyncio

from src.models import User
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
