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

    # Backfill from existing blockchain hashes to prevent rebroadcast
    # This prevents historical purchases from being sent again
    op.execute("""
        UPDATE transactions t
        SET outgoing_message_hash = tt.hash,
            sent_at = t.created_at
        FROM ton_transactions tt
        WHERE t.ton_transaction_id = tt.id
          AND tt.hash IS NOT NULL
          AND t.outgoing_message_hash IS NULL
    """)


def downgrade() -> None:
    op.drop_column("transactions", "outgoing_message_hash")
    op.drop_column("transactions", "sent_at")
