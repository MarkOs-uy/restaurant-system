"""create event_outbox

Revision ID: 6e40084bfae8
Revises: 6ba12f28852f
Create Date: 2026-05-05 18:52:54.136588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e40084bfae8'
down_revision: Union[str, Sequence[str], None] = '6ba12f28852f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # =============================
    # CREAR TABLA EVENT_OUTBOX
    # =============================

    op.create_table(
        "event_outbox",

        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "restaurant_id",
            sa.Integer(),
            sa.ForeignKey("restaurants.id"),
            nullable=False
        ),

        sa.Column(
            "event_type",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "payload",
            sa.JSON(),
            nullable=False
        ),

        sa.Column(
            "target",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "target_id",
            sa.String(),
            nullable=True
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="pending"
        ),

        sa.Column(
            "retries",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),

        sa.Column(
            "processed_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),

        sa.Column(
            "last_error",
            sa.String(),
            nullable=True
        ),
    )


    # =============================
    # INDEXES
    # =============================

    op.create_index(
        "ix_event_outbox_restaurant",
        "event_outbox",
        ["restaurant_id"]
    )

    op.create_index(
        "ix_event_outbox_status",
        "event_outbox",
        ["status"]
    )

    op.create_index(
        "ix_event_outbox_created",
        "event_outbox",
        ["created_at"]
    )

    op.create_index(
        "ix_event_outbox_event_type",
        "event_outbox",
        ["event_type"]
    )

    # --------------------------------------
    # Índice para cleanup de eventos enviados
    # --------------------------------------

    op.create_index(
        "idx_event_outbox_cleanup",
        "event_outbox",
        ["status", "processed_at"]
    )

    # --------------------------------------
    # Índice para cleanup de eventos fallidos
    # --------------------------------------

    op.create_index(
        "idx_event_outbox_failed_cleanup",
        "event_outbox",
        ["status", "retries", "created_at"]
    )


    # =============================
    # ELIMINAR DOMAIN_EVENTS
    # =============================

    op.drop_table("domain_events")


def downgrade():

    # =============================
    # RECREAR DOMAIN_EVENTS
    # =============================

    op.create_table(
        "domain_events",

        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column(
            "restaurant_id",
            sa.Integer(),
            sa.ForeignKey("restaurants.id"),
            nullable=False
        ),

        sa.Column(
            "event_type",
            sa.String(),
            nullable=True
        ),

        sa.Column(
            "payload",
            sa.JSON(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
    )


    # =============================
    # ELIMINAR EVENT_OUTBOX
    # =============================

    op.drop_index("ix_event_outbox_event_type", table_name="event_outbox")
    op.drop_index("ix_event_outbox_created", table_name="event_outbox")
    op.drop_index("ix_event_outbox_status", table_name="event_outbox")
    op.drop_index("ix_event_outbox_restaurant", table_name="event_outbox")

    op.drop_table("event_outbox")