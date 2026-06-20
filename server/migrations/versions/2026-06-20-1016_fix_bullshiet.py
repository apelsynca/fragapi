"""some_bullshiet_forgore

Revision ID: 9207c8bcf3d5
Revises: 5cd172428f8f
Create Date: 2026-06-20 07:47:56.030702

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9997c8bcf3d5"
down_revision: str | Sequence[str] | None = "9207c8bcf3d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("deposits", "payments")
    op.rename_table("transactions", "fragment_transactions")
    op.rename_table("ton_transactions", "transactions")


def downgrade() -> None:
    op.rename_table("payments", "deposits")
    op.rename_table("fragment_transactions", "transactions")
    op.rename_table("transactions", "ton_transactions")
