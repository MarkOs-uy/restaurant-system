from pydantic import Field

from .base import BaseSchema

class LayoutOut(BaseSchema):
    restaurant_id: int
    width: int
    height: int
    grid_size: int
    snap_to_grid: bool
    background_image: str | None = None


class LayoutUpdate(BaseSchema):
    width: int | None = None
    height: int | None = None
    grid_size: int | None = None
    snap_to_grid: bool | None = None
    background_image: str | None = None