import uuid
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    ForeignKey,
    String,
    UniqueConstraint,
    Index
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    number = Column(Integer, nullable=False)

    active = Column(Boolean, default=True, nullable=False)

    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)

    capacity = Column(Integer, default=4, nullable=False)

    shape = Column(String, default="Circular")

    external_id = Column(
        String,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )

    # 🔐 Multi-tenant constraints correctas
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

    # Relaciones
    orders = relationship(
        "Order",
        back_populates="table"
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="tables"
    )