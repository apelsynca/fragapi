"""sussibaka

Revision ID: a82a1107eabf
Revises: 8f3514c810c7
Create Date: 2026-01-02 05:02:25.986237

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a82a1107eabf"
down_revision: str | Sequence[str] | None = "8f3514c810c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "transactions", sa.Column("tx_hash", sa.String(length=64), nullable=True)
    )
    op.add_column(
        "transactions",
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "COMPLETED",
                "FAILED",
                name="transactionstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
    )
    op.add_column(
        "transactions", sa.Column("stars_quantity", sa.Integer(), nullable=True)
    )
    op.add_column(
        "transactions", sa.Column("recipient", sa.String(length=255), nullable=True)
    )
    op.create_index(
        op.f("ix_transactions_tx_hash"), "transactions", ["tx_hash"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_transactions_tx_hash"), table_name="transactions")
    op.drop_column("transactions", "recipient")
    op.drop_column("transactions", "stars_quantity")
    op.drop_column("transactions", "status")
    op.drop_column("transactions", "tx_hash")
