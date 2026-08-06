"""add more and more backup settings

Revision ID: 27cc3e563d72
Revises: 85d684a75027
Create Date: 2026-06-28 20:33:57.475524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27cc3e563d72'
down_revision: Union[str, Sequence[str], None] = '85d684a75027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column(
        "system_settings",
        sa.Column(
            "last_automatic_backup_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "next_automatic_backup_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "last_backup_result",
            sa.String(),
            nullable=True,
        ),
    )

    op.drop_column("system_settings", "backup_next_run")
    op.drop_column("system_settings", "backup_last_run")

def downgrade():

    op.drop_column(
        "system_settings",
        "next_automatic_backup_at",
    )

    op.drop_column(
        "system_settings",
        "last_automatic_backup_at",
    )

    op.drop_column(
        "system_settings",
        "last_backup_result",
    )