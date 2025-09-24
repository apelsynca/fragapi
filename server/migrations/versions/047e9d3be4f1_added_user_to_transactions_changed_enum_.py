"""added user to transactions, changed enum type

Revision ID: 047e9d3be4f1
Revises: f9f23ecd7b7b
Create Date: 2025-08-24 08:28:56.510642

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "047e9d3be4f1"
down_revision: str | Sequence[str] | None = "f9f23ecd7b7b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("transactions", sa.Column("user_id", sa.BigInteger(), nullable=False))
    op.alter_column(
        "transactions",
        "reason",
        existing_type=postgresql.ENUM("STARS", name="transactionreason"),
        type_=sa.Enum("PREMIUM", "STARS", name="transactionreason", native_enum=False),
        existing_nullable=False,
    )
    op.create_foreign_key(None, "transactions", "users", ["user_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "transactions", type_="foreignkey")
    op.alter_column(
        "transactions",
        "reason",
        existing_type=sa.Enum(
            "PREMIUM", "STARS", name="transactionreason", native_enum=False
        ),
        type_=postgresql.ENUM("STARS", name="transactionreason"),
        existing_nullable=False,
    )
    op.drop_column("transactions", "user_id")
