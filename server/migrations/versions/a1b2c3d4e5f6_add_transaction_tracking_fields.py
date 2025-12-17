"""add transaction tracking fields

Revision ID: a1b2c3d4e5f6
Revises: 047e9d3be4f1
Create Date: 2025-12-17 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "047e9d3be4f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add tx_hash column for blockchain transaction hash
    op.add_column(
        "transactions",
        sa.Column("tx_hash", sa.String(64), nullable=True, index=True),
    )

    # Add status column for transaction verification
    op.add_column(
        "transactions",
        sa.Column(
            "status",
            sa.Enum("PENDING", "COMPLETED", "FAILED", name="transactionstatus", native_enum=False),
            nullable=False,
            server_default="pending",
        ),
    )

    # Add stars_quantity for tracking how many stars were purchased
    op.add_column(
        "transactions",
        sa.Column("stars_quantity", sa.Integer(), nullable=True),
    )

    # Add recipient for tracking who received the stars/premium
    op.add_column(
        "transactions",
        sa.Column("recipient", sa.String(255), nullable=True),
    )

    # Create index on tx_hash for faster lookups
    op.create_index("ix_transactions_tx_hash", "transactions", ["tx_hash"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_transactions_tx_hash", table_name="transactions")
    op.drop_column("transactions", "recipient")
    op.drop_column("transactions", "stars_quantity")
    op.drop_column("transactions", "status")
    op.drop_column("transactions", "tx_hash")

