from pydantic import BaseModel
from datetime import datetime


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # reemplaza orm_mode en Pydantic v2


class TimestampSchema(BaseSchema):
    created_at: datetime