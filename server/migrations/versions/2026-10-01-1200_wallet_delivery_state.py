"""Store outgoing message hashes and submission timestamps.

Revision ID: b82bdbf80731
Revises: cd0eb48de5b2
"""

import sqlalchemy as sa
from alembic import op

revision = "b82bdbf80731"
down_revision = "cd0eb48de5b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("transactions", sa.Column("sent_at", sa.DateTime(timezone=True)))
    op.add_column("transactions", sa.Column("outgoing_message_hash", sa.String()))


def downgrade() -> None:
    for name in (
        "outgoing_message_hash",
        "sent_at",
    ):
        op.drop_column("transactions", name)
