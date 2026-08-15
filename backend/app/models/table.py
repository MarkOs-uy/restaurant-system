import uuid

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
    Index,
    Identity
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base

from app.models.enums import TableShape


class Table(Base):
    __tablename__ = "tables"

    id = Column(
        Integer,
        Identity(),
        primary_key=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    number = Column(
        Integer,
        nullable=False
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    x = Column(
        Integer,
        nullable=False,
        default=0
    )

    y = Column(
        Integer,
        nullable=False,
        default=0
    )

    capacity = Column(
        Integer,
        nullable=False,
        default=4
    )

    shape = Column(
        String,
        nullable=False,
        default=TableShape.CIRCLE.value
    )

    external_id = Column(
        String,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "number",
            name="uq_table_number_per_restaurant"
        ),
        UniqueConstraint(
            "restaurant_id",
            "external_id",
            name="uq_table_external_per_restaurant"
        ),
        Index(
            "ix_table_restaurant_active",
            "restaurant_id",
            "active"
        ),
    )

    orders = relationship(
        "Order",
        back_populates="table"
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="tables"
    )