import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.fragment_transactions.repository import TransactionRepository

from src.auth.scope import Scope
from src.models import FragmentTransaction, User
from tests.fixtures.auth import AuthSubjectFixture
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_transaction


@pytest.mark.asyncio
async def test_unauthorized_201(client: AsyncClient) -> None:
    response = await client.get("/v1/transactions/")
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.auth(
    AuthSubjectFixture(subject="user", scopes={Scope.api, Scope.transactions_read}),
    AuthSubjectFixture(subject="user", scopes={Scope.web, Scope.transactions_read}),
)
async def test_gets_all_transactions(
    session: AsyncSession, client: AsyncClient, user: User, save_fixture: SaveFixture
) -> None:
    repository = TransactionRepository.from_session(session)

    stmt = repository.get_base_stmt().where(FragmentTransaction.user == user)
    trans_count = await repository.count(stmt=stmt)
    assert trans_count == 0

    await create_transaction(save_fixture, user=user)
    await create_transaction(save_fixture, user=user)
    await create_transaction(save_fixture, user=user)

    response = await client.get("/v1/transactions/")
    assert response.status_code == 200

    json = response.json()

    assert "items" in json
    assert "pagination" in json

    assert len(json["items"]) == 3
