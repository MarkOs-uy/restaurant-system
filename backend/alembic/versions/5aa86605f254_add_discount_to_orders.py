"""add discount to orders

Revision ID: 5aa86605f254
Revises: 7b0b567ffe9e
Create Date: 2026-03-18 18:02:40.042295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5aa86605f254'
down_revision: Union[str, Sequence[str], None] = '7b0b567ffe9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'orders',
        sa.Column('discount', sa.Numeric(10, 2), nullable=False, server_default="0")
    )
    
    op.alter_column('orders', 'discount', server_default=None)


def downgrade() -> None:
    op.drop_column('orders', 'discount')
