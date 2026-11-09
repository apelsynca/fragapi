"""stars bulk purchases

Revision ID: 5e1c0b7a9d42
Revises: b82bdbf80731
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "5e1c0b7a9d42"
down_revision = "b82bdbf80731"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stars_bulk_purchases",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "charged",
                "done",
                name="bulkpurchasestatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("items", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_stars_bulk_purchases_created_at"),
        "stars_bulk_purchases",
        ["created_at"],
    )
    op.create_index(
        op.f("ix_stars_bulk_purchases_user_id"), "stars_bulk_purchases", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stars_bulk_purchases_user_id"), "stars_bulk_purchases")
    op.drop_index(op.f("ix_stars_bulk_purchases_created_at"), "stars_bulk_purchases")
    op.drop_table("stars_bulk_purchases")
