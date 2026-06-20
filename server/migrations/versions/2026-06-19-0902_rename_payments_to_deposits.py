"""some_bullshiet

Revision ID: 5cd172428f8f
Revises: fccb267549ff
Create Date: 2026-06-19 09:02:52.068331

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5cd172428f8f"
down_revision: str | Sequence[str] | None = "fccb267549ff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("payments", "deposits")


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table("deposits", "payments")
