import importlib.util
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Connection, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User


@pytest.mark.asyncio
async def test_migration_preserves_existing_users(
    session: AsyncSession, user: User
) -> None:
    path = (
        Path(__file__).parents[2]
        / "migrations/versions/2026-11-19-1200_signup_attribution.py"
    )
    spec = importlib.util.spec_from_file_location("signup_attribution_migration", path)
    assert spec is not None
    assert spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    def roundtrip(connection: Connection) -> None:
        with Operations.context(MigrationContext.configure(connection)):
            migration.downgrade()
            assert "signup_source" not in {
                c["name"] for c in inspect(connection).get_columns("users")
            }
            migration.upgrade()
        assert "ix_users_signup_source" in {
            i["name"] for i in inspect(connection).get_indexes("users")
        }

    connection = await session.connection()
    await connection.run_sync(roundtrip)
    await session.refresh(user)
    assert user.signup_source is None
    assert user.signup_medium is None
    assert user.signup_campaign is None
    assert user.signup_referrer is None
