from sqlalchemy.orm import Session
from app.models.restaurant_layout import RestaurantLayout
from app.schemas.layout import LayoutUpdate
import logging

logger = logging.getLogger("app.domain.layout")


class LayoutService:

    def __init__(self, db: Session):
        self.db = db


    def get_layout(self, restaurant_id: int):

        layout = (
            self.db.query(RestaurantLayout)
            .filter(RestaurantLayout.restaurant_id == restaurant_id)
            .first()
        )

        if not layout:

            layout = RestaurantLayout(
                restaurant_id=restaurant_id,
                width=900,
                height=750,
                grid_size=40,
                snap_to_grid=True
            )

            self.db.add(layout)
            self.db.commit()
            self.db.refresh(layout)

        return layout


    def update_layout(self, restaurant_id: int, data: LayoutUpdate):
        logger.info("Layout actualizado r=%s", restaurant_id)
        layout = self.get_layout(restaurant_id)

        layout.width = data.width
        layout.height = data.height
        layout.grid_size = data.grid_size
        layout.snap_to_grid = data.snap_to_grid

        self.db.commit()
        self.db.refresh(layout)

        return layout