"""add draft status to orderstatus

Revision ID: 0d21e3868b2f
Revises: 5aa86605f254
Create Date: 2026-03-22 15:34:58.319184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d21e3868b2f'
down_revision: Union[str, Sequence[str], None] = '5aa86605f254'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE orderstatus ADD VALUE 'DRAFT'")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
