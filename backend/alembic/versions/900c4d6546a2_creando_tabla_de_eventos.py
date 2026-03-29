"""creando tabla de eventos

Revision ID: 900c4d6546a2
Revises: 0d21e3868b2f
Create Date: 2026-03-26 17:33:05.954838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '900c4d6546a2'
down_revision: Union[str, Sequence[str], None] = '0d21e3868b2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "domain_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("domain_events")
