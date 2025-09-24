"""user_agent is optional for session

Revision ID: 8f3514c810c7
Revises: 7e57eaa0fbb7
Create Date: 2025-08-31 17:20:31.709717

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8f3514c810c7"
down_revision: str | Sequence[str] | None = "7e57eaa0fbb7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "user_sessions", "user_agent", existing_type=sa.TEXT(), nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "user_sessions", "user_agent", existing_type=sa.TEXT(), nullable=False
    )
