from typing import Optional
from .base import BaseSchema
from app.models.user import UserRole


class UserCreate(BaseSchema):
    username: str
    password: str
    role: UserRole


class UserUpdate(BaseSchema):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class UserOut(BaseSchema):
    id: int
    username: str
    role: UserRole
    active: bool