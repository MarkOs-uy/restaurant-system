from sqlalchemy import Column, Integer, String, JSON, DateTime, func, ForeignKey, Identity
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class DomainEvent(Base):

    __tablename__ = "domain_events"

    id = Column(Integer, Identity(), primary_key=True, index=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )

    event_type = Column(String, nullable=False)

    payload = Column(JSON)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="domain_events"
    )