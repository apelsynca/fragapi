"""fix_for_the_transaction_refactor_p2

Revision ID: f8ab285d7b48
Revises: baba3f4c466e
Create Date: 2026-06-20 14:27:06.736025

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8ab285d7b48"
down_revision: str | Sequence[str] | None = "baba3f4c466e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("deposits", "transaction_id", new_column_name="ton_transaction_id")
    op.alter_column(
        "fragment_transactions", "transaction_id", new_column_name="ton_transaction_id"
    )

    # --- fragment_transactions -> transactions

    op.execute("ALTER INDEX fragment_transactions_pkey RENAME TO transactions_pkey")
    op.execute(
        "ALTER INDEX fragment_transactions_transaction_id_key RENAME TO transactions_transaction_id"
    )
    op.execute(
        "ALTER INDEX ix_fragment_transactions_created_at RENAME TO transactions_created_at"
    )

    op.rename_table("fragment_transactions", "transactions")


def downgrade() -> None:
    op.rename_table("transactions", "fragment_transactions")

    op.execute(
        "ALTER INDEX transactions_created_at RENAME TO ix_fragment_transactions_created_at"
    )
    op.execute(
        "ALTER INDEX transactions_transaction_id RENAME TO fragment_transactions_transaction_id_key"
    )
    op.execute("ALTER INDEX transactions_pkey RENAME TO fragment_transactions_pkey")

    op.alter_column(
        "fragment_transactions", "ton_transaction_id", new_column_name="transaction_id"
    )
    op.alter_column("deposits", "ton_transaction_id", new_column_name="transaction_id")
