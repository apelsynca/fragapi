"""user.is_premium user_session.bot_hash

Revision ID: 7e57eaa0fbb7
Revises: 047e9d3be4f1
Create Date: 2025-08-31 17:18:26.977237

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e57eaa0fbb7"
down_revision: str | Sequence[str] | None = "047e9d3be4f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("user_sessions", sa.Column("bot_hash", sa.String(), nullable=True))
    op.create_unique_constraint(None, "user_sessions", ["bot_hash"])
    op.add_column(
        "users",
        sa.Column("is_premium", sa.Boolean(), nullable=False, server_default="FALSE"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "is_premium")
    op.drop_constraint("bot_hash", "user_sessions", type_="unique")
    op.drop_column("user_sessions", "bot_hash")
