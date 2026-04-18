from .base import BaseSchema

class LayoutOut(BaseSchema):
    width: int
    height: int
    grid_size: int
    snap_to_grid: bool


class LayoutUpdate(BaseSchema):
    width: int
    height: int
    grid_size: int
    snap_to_grid: bool