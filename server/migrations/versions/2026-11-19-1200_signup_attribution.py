"""Persist signup attribution on users.

Revision ID: 8b25da9e6c10
Revises: 3a9f6c2e17d4
"""

import sqlalchemy as sa
from alembic import op

revision = "8b25da9e6c10"
down_revision = "3a9f6c2e17d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name in ("source", "medium", "campaign", "referrer"):
        op.add_column("users", sa.Column(f"signup_{name}", sa.String(), nullable=True))
    op.create_index("ix_users_signup_source", "users", ["signup_source"])


def downgrade() -> None:
    op.drop_index("ix_users_signup_source", table_name="users")
    for name in ("referrer", "campaign", "medium", "source"):
        op.drop_column("users", f"signup_{name}")
