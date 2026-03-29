"""agregar índice a tabla de eventos por restaurant_id

Revision ID: e2398672eb07
Revises: 900c4d6546a2
Create Date: 2026-03-26 17:46:46.648977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2398672eb07'
down_revision: Union[str, Sequence[str], None] = '900c4d6546a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_domain_events_restaurant",
        "domain_events",
        ["restaurant_id"]
    )



def downgrade() -> None:
    op.drop_index(
        "idx_domain_events_restaurant",
        table_name="domain_events"
    )
