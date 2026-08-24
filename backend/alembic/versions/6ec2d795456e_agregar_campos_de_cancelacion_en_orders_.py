"""agregar campos de cancelacion en orders y order-items

Revision ID: 6ec2d795456e
Revises: f2b920bbec2b
Create Date: 2026-08-21 10:52:39.282688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ec2d795456e'
down_revision: Union[str, Sequence[str], None] = 'f2b920bbec2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------
    # Orders
    # --------------------------------------------------
    op.add_column(
        "orders",
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.add_column(
        "orders",
        sa.Column(
            "cancelled_by_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "orders",
        sa.Column(
            "cancellation_reason",
            sa.Text(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_orders_cancelled_by_id_users",
        "orders",
        "users",
        ["cancelled_by_id"],
        ["id"]
    )


    # --------------------------------------------------
    # Order items
    # --------------------------------------------------
    op.add_column(
        "order_items",
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.add_column(
        "order_items",
        sa.Column(
            "cancelled_by_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "order_items",
        sa.Column(
            "cancellation_reason",
            sa.Text(),
            nullable=True
        )
    )

    op.create_foreign_key(
        "fk_order_items_cancelled_by_id_users",
        "order_items",
        "users",
        ["cancelled_by_id"],
        ["id"]
    )


def downgrade() -> None:
    # --------------------------------------------------
    # Order items
    # --------------------------------------------------
    op.drop_constraint(
        "fk_order_items_cancelled_by_id_users",
        "order_items",
        type_="foreignkey"
    )

    op.drop_column(
        "order_items",
        "cancellation_reason"
    )

    op.drop_column(
        "order_items",
        "cancelled_by_id"
    )

    op.drop_column(
        "order_items",
        "cancelled_at"
    )


    # --------------------------------------------------
    # Orders
    # --------------------------------------------------
    op.drop_constraint(
        "fk_orders_cancelled_by_id_users",
        "orders",
        type_="foreignkey"
    )

    op.drop_column(
        "orders",
        "cancellation_reason"
    )

    op.drop_column(
        "orders",
        "cancelled_by_id"
    )

    op.drop_column(
        "orders",
        "cancelled_at"
    )