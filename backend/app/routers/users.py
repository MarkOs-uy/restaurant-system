"""
Endpoints para la gestión de los usuarios del sistema.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import APIRouter, Depends, status

from app.dependencies.roles import admin_only

from app.domain.user.user_service import UserService
from app.domain.user.dependencies import get_user_service

from app.models.user import User

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserOut
)

router = APIRouter(prefix="/users", tags=["users"])

# ----------------------------------------------------------------------------------------------------
# Crear usuario
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un usuario en el sistema."
)
def create_user(
    data: UserCreate,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Listar usuarios del sistema
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Lista los usuarios del sistema."
)
def list_users(
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.list_users(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Actualiza un usuario
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario",
    description="Actualiza un usuario del sistema."
)
def update_user(
    user_id: int,
    data: UserUpdate,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(user_id, user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Activa/Desactiva un usuario
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{user_id}/toggle",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Activar/Desactivar usuario",
    description="Activa o desactiva a un usuario del sistema."
)
def toggle_user(
    user_id: int,
    user: User = Depends(admin_only),
    service: UserService = Depends(get_user_service)
):
    return service.toggle_user(user_id, user.id, user.restaurant_id)