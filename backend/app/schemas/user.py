from .base import BaseSchema
from app.models.user import UserRole

class UserOut(BaseSchema):
    id: int
    username: str
    role: UserRole
    active: bool