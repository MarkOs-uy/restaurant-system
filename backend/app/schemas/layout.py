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
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    grid_size: int = Field(gt=0)
    snap_to_grid: bool