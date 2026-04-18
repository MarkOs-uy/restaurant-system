"""cambios en cashregister

Revision ID: 6ba12f28852f
Revises: 7fd07db91f0d
Create Date: 2026-03-31 03:06:33.845028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ba12f28852f'
down_revision: Union[str, Sequence[str], None] = '7fd07db91f0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cash_registers",
        sa.Column("expected_cash", sa.Numeric(10,2), nullable=True)
    )

    op.add_column(
        "cash_registers",
        sa.Column("counted_cash", sa.Numeric(10,2), nullable=True)
    )

    op.add_column(
        "cash_registers",
        sa.Column("difference", sa.Numeric(10,2), nullable=True)
    )

    op.add_column(
        "cash_registers",
        sa.Column("total_sales", sa.Numeric(10,2), nullable=True)
    )

    op.add_column(
        "cash_registers",
        sa.Column("payments_snapshot", sa.JSON(), nullable=True)
    )

    op.create_table(
        "cash_movements",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "cash_register_id",
            sa.Integer(),
            sa.ForeignKey("cash_registers.id"),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False
        ),

        sa.Column(
            "type",
            sa.String(length=20),
            nullable=False
        ),

        sa.Column(
            "amount",
            sa.Numeric(10,2),
            nullable=False
        ),

        sa.Column(
            "reason",
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        )
    )

    op.create_index(
        "ix_cash_movements_register",
        "cash_movements",
        ["cash_register_id"]
    )

    op.create_index(
        "ix_cash_movements_register_type",
        "cash_movements",
        ["cash_register_id", "type"]
    )


def downgrade() -> None:
    op.drop_index("ix_cash_movements_register_type", table_name="cash_movements")
    op.drop_index("ix_cash_movements_register", table_name="cash_movements")

    op.drop_table("cash_movements")

    op.drop_column("cash_registers", "payments_snapshot")
    op.drop_column("cash_registers", "total_sales")
    op.drop_column("cash_registers", "difference")
    op.drop_column("cash_registers", "counted_cash")
    op.drop_column("cash_registers", "expected_cash")