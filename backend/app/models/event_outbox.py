from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    ForeignKey,
    Identity,
    func
)

from sqlalchemy.orm import relationship
from app.db.base_class import Base

class EventOutbox(Base):

    __tablename__ = "event_outbox"

    id = Column(Integer, Identity(), primary_key=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    event_type = Column(
        String,
        nullable=False,
        index=True
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
        default="pending",
        index=True
    )

    retries = Column(
        Integer,
        nullable=False,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    last_error = Column(
        String,
        nullable=True
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="event_outbox"
    )