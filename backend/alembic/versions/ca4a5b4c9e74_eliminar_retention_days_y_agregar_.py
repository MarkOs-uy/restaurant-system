"""eliminar retention days y agregar retention daily, weekly y monthly en system_settings

Revision ID: ca4a5b4c9e74
Revises: fdb697085b8d
Create Date: 2026-07-18 17:04:07.755058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca4a5b4c9e74'
down_revision: Union[str, Sequence[str], None] = 'fdb697085b8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "system_settings",
        sa.Column(
            "backup_retention_daily",
            sa.Integer(),
            nullable=False,
            server_default="30"
        )
    )
    op.add_column(
        "system_settings",
        sa.Column(
            "backup_retention_weekly",
            sa.Integer(),
            nullable=False,
            server_default="12"
        )
    )
    op.add_column(
        "system_settings",
        sa.Column(
            "backup_retention_monthly",
            sa.Integer(),
            nullable=False,
            server_default="24"
        )
    )

    op.drop_column("system_settings", "backup_retention_days")

def downgrade() -> None:
    op.add_column(
        "system_settings",
        sa.Column(
            "backup_retention_days",
            sa.Integer(),
            nullable=False,
            server_default="30"
        )
    )

    op.drop_column("system_settings", "backup_retention_daily")
    op.drop_column("system_settings", "backup_retention_weekly")
    op.drop_column("system_settings", "backup_retention_monthly")
