from fastapi import APIRouter, Depends

from app.dependencies.roles import admin_only

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserOut

from app.domain.user.user_service import UserService
from app.domain.user.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut)
def create_user(
    data: UserCreate,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user.restaurant_id, data)


@router.get("/", response_model=list[UserOut])
def list_users(
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.list_users(user.restaurant_id)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(user_id, user.restaurant_id, data)


@router.patch("/{user_id}/toggle", response_model=UserOut)
def toggle_user(
    user_id: int,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.toggle_user(user_id, user.restaurant_id)