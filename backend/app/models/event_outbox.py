from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    Identity,
    Index,
    func
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class EventOutbox(Base):
    __tablename__ = "event_outbox"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )

    event_type = Column(
        String,
        nullable=False
    )

    payload = Column(
        JSON,
        nullable=False
    )

    target = Column(
        String,
        nullable=False
    )

    target_id = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="pending"
    )

    retries = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    last_error = Column(
        String,
        nullable=True
    )

    __table_args__ = (
        Index(
            "ix_event_outbox_restaurant",
            "restaurant_id"
        ),
        Index(
            "ix_event_outbox_event_type",
            "event_type"
        ),
        Index(
            "ix_event_outbox_status",
            "status"
        ),
        Index(
            "ix_event_outbox_created",
            "created_at"
        ),
        Index(
            "idx_event_outbox_cleanup",
            "status",
            "processed_at"
        ),
        Index(
            "idx_event_outbox_failed_cleanup",
            "status",
            "retries",
            "created_at"
        ),
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="event_outbox"
    )