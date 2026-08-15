"""category active and product station constraints(2)

Revision ID: a5fb39b05ac8
Revises: ca4a5b4c9e74
Create Date: 2026-08-12 02:20:46.787954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a5fb39b05ac8'
down_revision: Union[str, Sequence[str], None] = 'ca4a5b4c9e74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # -------------------------------------------------------------------------
    # Agrega baja lógica a categorías.
    # Las categorías existentes se consideran activas.
    # -------------------------------------------------------------------------
    op.add_column(
        "categories",
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )

    # El default se utiliza únicamente para migrar las filas existentes.
    op.alter_column(
        "categories",
        "active",
        server_default=None
    )

    # -------------------------------------------------------------------------
    # Las estaciones siempre deben tener un estado activo/inactivo definido.
    # -------------------------------------------------------------------------
    op.alter_column(
        "production_stations",
        "active",
        existing_type=sa.BOOLEAN(),
        nullable=False
    )

    # -------------------------------------------------------------------------
    # Los productos siempre deben tener estado, categoría y estación.
    # -------------------------------------------------------------------------
    op.alter_column(
        "products",
        "active",
        existing_type=sa.BOOLEAN(),
        nullable=False
    )

    op.alter_column(
        "products",
        "station_id",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        "products",
        "category_id",
        existing_type=sa.INTEGER(),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "products",
        "category_id",
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.alter_column(
        "products",
        "station_id",
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.alter_column(
        "products",
        "active",
        existing_type=sa.BOOLEAN(),
        nullable=True
    )

    op.alter_column(
        "production_stations",
        "active",
        existing_type=sa.BOOLEAN(),
        nullable=True
    )

    op.drop_column(
        "categories",
        "active"
    )