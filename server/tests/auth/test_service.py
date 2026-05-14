import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import auth as auth_service
from src.exceptions import Forbidden
from tests.fixtures.random_objects import rstr


@pytest.mark.asyncio
async def test_login_by_bot_hash_random_raises(session: AsyncSession) -> None:
    with pytest.raises(Forbidden):
        await auth_service.login_by_bot_hash(
            session=session, bot_hash=rstr("someWrong")
        )
