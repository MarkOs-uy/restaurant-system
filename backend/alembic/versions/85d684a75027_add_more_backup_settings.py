"""add more backup settings

Revision ID: 85d684a75027
Revises: 1b3cb23f2af7
Create Date: 2026-06-28 16:38:19.706936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85d684a75027'
down_revision: Union[str, Sequence[str], None] = '1b3cb23f2af7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_frequency",
            sa.String(),
            nullable=False,
            server_default="manual"
        )
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_retention_days",
            sa.Integer(),
            nullable=False,
            server_default="30"
        )
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_last_run",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_next_run",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )


def downgrade():

    op.drop_column("system_settings", "backup_next_run")
    op.drop_column("system_settings", "backup_last_run")
    op.drop_column("system_settings", "backup_enabled")
    op.drop_column("system_settings", "backup_retention_days")
    op.drop_column("system_settings", "backup_frequency")
