from sqlalchemy import Column, Integer, Boolean, ForeignKey, String
from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )

    restaurant = relationship("Restaurant", back_populates="categories")
    products = relationship("Product", back_populates="category")

