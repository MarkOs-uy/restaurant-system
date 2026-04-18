"""refactor restaurant_layout structure

Revision ID: 7fd07db91f0d
Revises: a4b707b32039
Create Date: 2026-03-30 02:44:25.946302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fd07db91f0d'
down_revision: Union[str, Sequence[str], None] = 'a4b707b32039'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # eliminar PK actual
    op.drop_constraint(
        "restaurant_layout_pkey",
        "restaurant_layout",
        type_="primary"
    )

    # eliminar columna id
    op.drop_column("restaurant_layout", "id")

    # convertir restaurant_id en PK
    op.create_primary_key(
        "restaurant_layout_pkey",
        "restaurant_layout",
        ["restaurant_id"]
    )

    # nuevos campos
    op.add_column(
        "restaurant_layout",
        sa.Column("grid_size", sa.Integer(), server_default="40")
    )

    op.add_column(
        "restaurant_layout",
        sa.Column("snap_to_grid", sa.Boolean(), server_default="true")
    )

    op.add_column(
        "restaurant_layout",
        sa.Column("background_image", sa.String(), nullable=True)
    )


def downgrade():

    op.drop_column("restaurant_layout", "background_image")
    op.drop_column("restaurant_layout", "snap_to_grid")
    op.drop_column("restaurant_layout", "grid_size")

    op.drop_constraint(
        "restaurant_layout_pkey",
        "restaurant_layout",
        type_="primary"
    )

    op.add_column(
        "restaurant_layout",
        sa.Column("id", sa.Integer(), primary_key=True)
    )

    op.create_primary_key(
        "restaurant_layout_pkey",
        "restaurant_layout",
        ["id"]
    )