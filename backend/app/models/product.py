from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, UniqueConstraint, Identity
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, Identity(), primary_key=True)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    station_id = Column(
        Integer,
        ForeignKey("production_stations.id"),
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )
    
    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_product_name_per_restaurant"),
    )

    category = relationship("Category", back_populates="products")
    station = relationship("ProductionStation", back_populates="products")
    restaurant = relationship("Restaurant", back_populates="products")

