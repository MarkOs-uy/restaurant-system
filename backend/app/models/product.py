from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True)
    restaurant = relationship("Restaurant", back_populates="products")

