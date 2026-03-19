"""add discount to orders

Revision ID: 7b0b567ffe9e
Revises: 50f5f9de1220
Create Date: 2026-03-18 18:02:00.580785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b0b567ffe9e'
down_revision: Union[str, Sequence[str], None] = '50f5f9de1220'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
