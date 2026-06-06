import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.schemas import UserCreate
from src.user.service import user as user_service


@pytest.mark.asyncio
async def test_user_create(session: AsyncSession) -> None:
    new_user = await user_service.create(
        session=session,
        data=UserCreate(
            id=19999, first_name="Any Name", last_name=None, username="someusername"
        ),
    )

    assert new_user.id == 19999
    assert new_user.first_name == "Any Name"
    assert new_user.last_name is None
    assert new_user.username == "someusername"
