"""Let purchases sent in one wallet message share the chain hash.

Revision ID: 3a9f6c2e17d4
Revises: 5e1c0b7a9d42
"""

import sqlalchemy as sa
from alembic import op

revision = "3a9f6c2e17d4"
down_revision = "5e1c0b7a9d42"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_ton_transactions_hash", table_name="ton_transactions")
    op.create_index(
        "ix_ton_transactions_hash", "ton_transactions", ["hash"], unique=False
    )
    # Deposits have no message hash: one incoming chain transaction, one row.
    op.create_index(
        "uq_ton_transactions_deposit_hash",
        "ton_transactions",
        ["hash"],
        unique=True,
        postgresql_where=sa.text("message_hash IS NULL"),
    )

    # Earlier bulks stored the hash on the first purchase only.
    op.execute("""
        UPDATE ton_transactions tt
        SET hash = bulk.hash
        FROM transactions t
        JOIN (
            SELECT t2.outgoing_message_hash, max(tt2.hash) AS hash
            FROM transactions t2
            JOIN ton_transactions tt2 ON tt2.id = t2.ton_transaction_id
            WHERE t2.outgoing_message_hash IS NOT NULL
              AND tt2.hash IS NOT NULL
            GROUP BY t2.outgoing_message_hash
        ) bulk ON bulk.outgoing_message_hash = t.outgoing_message_hash
        WHERE t.ton_transaction_id = tt.id
          AND tt.hash IS NULL
    """)


def downgrade() -> None:
    # The unique index allows one row per hash: keep the oldest of each bulk.
    op.execute("""
        UPDATE ton_transactions tt
        SET hash = NULL
        FROM (
            SELECT id, row_number() OVER (
                PARTITION BY hash ORDER BY created_at, id
            ) AS position
            FROM ton_transactions
            WHERE hash IS NOT NULL
        ) ranked
        WHERE ranked.id = tt.id
          AND ranked.position > 1
    """)
    op.drop_index("uq_ton_transactions_deposit_hash", table_name="ton_transactions")
    op.drop_index("ix_ton_transactions_hash", table_name="ton_transactions")
    op.create_index(
        "ix_ton_transactions_hash", "ton_transactions", ["hash"], unique=True
    )
