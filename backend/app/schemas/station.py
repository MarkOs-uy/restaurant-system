from .base import BaseSchema

class StationCreate(BaseSchema):
    name: str

class StationUpdate(BaseSchema):
    name: str

class StationRef(BaseSchema):
    id: int
    name: str

class StationResponse(BaseSchema):
    id: int
    name: str
    active: bool