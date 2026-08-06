"""add backup settings

Revision ID: 1b3cb23f2af7
Revises: 72a2554e30d4
Create Date: 2026-06-17 16:53:52.703166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b3cb23f2af7'
down_revision: Union[str, Sequence[str], None] = '72a2554e30d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_settings",

        sa.Column(
            "restaurant_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column("smtp_host", sa.String(), nullable=True),
        sa.Column("smtp_port", sa.Integer(), nullable=True),
        sa.Column("smtp_user", sa.String(), nullable=True),
        sa.Column("smtp_password", sa.String(), nullable=True),
        sa.Column("smtp_from", sa.String(), nullable=True),

        sa.Column(
            "smtp_use_tls",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        ),

        sa.Column("backup_email", sa.String(), nullable=True),

        sa.ForeignKeyConstraint(
            ["restaurant_id"],
            ["restaurants.id"],
            ondelete="CASCADE"
        ),

        sa.PrimaryKeyConstraint("restaurant_id")
    )

    op.create_index(
        "ix_order_items_order_status",
        "order_items",
        ["order_id", "status"]
    )

    op.alter_column(
        "orders",
        "closed_at",
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True
    )



def downgrade() -> None:

    op.alter_column(
        "orders",
        "closed_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=True
    )

    op.drop_index(
        "ix_order_items_order_status",
        table_name="order_items"
    )

    op.drop_table("system_settings")
