"""rename users.name to users.username

Revision ID: 72a2554e30d4
Revises: 6e40084bfae8
Create Date: 2026-05-20 21:50:28.197239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72a2554e30d4'
down_revision: Union[str, Sequence[str], None] = '6e40084bfae8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'name', new_column_name='username')

def downgrade() -> None:
    op.alter_column('users', 'username', new_column_name='name')
