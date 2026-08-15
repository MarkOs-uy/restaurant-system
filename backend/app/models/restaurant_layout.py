from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    ForeignKey
)

from app.db.base_class import Base


class RestaurantLayout(Base):
    __tablename__ = "restaurant_layout"

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        primary_key=True
    )

    width = Column(
        Integer,
        nullable=False,
        default=900
    )

    height = Column(
        Integer,
        nullable=False,
        default=500
    )

    grid_size = Column(
        Integer,
        nullable=False,
        default=40
    )

    snap_to_grid = Column(
        Boolean,
        nullable=False,
        default=True
    )

    background_image = Column(
        String,
        nullable=True
    )