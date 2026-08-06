"""add more and more and more backup settings

Revision ID: fdb697085b8d
Revises: 27cc3e563d72
Create Date: 2026-07-11 23:06:30.821779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdb697085b8d'
down_revision: Union[str, Sequence[str], None] = '27cc3e563d72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_time",
            sa.Time(),
            nullable=False,
            server_default="03:00:00",
        ),
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_weekday",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_monthday",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_keep_local",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_send_email",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "system_settings",
        sa.Column(
            "backup_timezone",
            sa.String(),
            nullable=False,
            server_default="America/Montevideo",
        ),
    )


def downgrade():

    op.drop_column(
        "system_settings",
        "backup_keep_local",
    )

    op.drop_column(
        "system_settings",
        "backup_monthday",
    )

    op.drop_column(
        "system_settings",
        "backup_weekday",
    )

    op.drop_column(
        "system_settings",
        "backup_time",
    )

    op.drop_column(
        "system_settings",
        "backup_send_email",
    )

    op.drop_column(
        "system_settings",
        "backup_timezone",
    )   