from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, UniqueConstraint
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True
    )
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    active = Column(Boolean, default=True)
    station_id = Column(ForeignKey("production_stations.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_product_name_per_restaurant"),
    )

    category = relationship("Category", back_populates="products")
    station = relationship("ProductionStation", back_populates="products")
    restaurant = relationship("Restaurant", back_populates="products")

