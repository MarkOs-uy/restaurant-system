from sqlalchemy import (
    Column,
    Integer,
    Boolean, 
    ForeignKey, 
    String, 
    UniqueConstraint, 
    Identity
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, Identity(), primary_key=True)

    name = Column(String, nullable=False)

    active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "name",
            name="uq_category_name_per_restaurant"
        ),
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="categories"
    )

    products = relationship(
        "Product",
        back_populates="category"
    )