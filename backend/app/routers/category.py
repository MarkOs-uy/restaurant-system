"""
Endpoints para la gestión de categorías.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import APIRouter, Depends, status, Query

from app.dependencies.roles import admin_only, waiter_or_admin

from app.domain.category.category_service import CategoryService
from app.domain.category.dependencies import get_category_service

from app.models.user import User

from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithProducts,
)

router = APIRouter(prefix="/categories", tags=["categories"])

# ----------------------------------------------------------------------------------------------------
# Crear categoría
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
    description="Crea una nueva categoría para el restaurante autenticado."
)
def create_category(
    data: CategoryCreate,
    user: User = Depends(admin_only),
    service: CategoryService = Depends(get_category_service),
):
    return service.create_category(user.restaurant_id, data)

# ----------------------------------------------------------------------------------------------------
# Listar categorías
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías",
    description="Devuelve la lista de categorías del restaurante autenticado."
)
def list_categories(
    active: bool | None = Query(default=True),
    user: User = Depends(waiter_or_admin),
    service: CategoryService = Depends(get_category_service)
):
    return service.list_categories(user.restaurant_id, active)

# ----------------------------------------------------------------------------------------------------
# Listar categorías con productos
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/with-products",
    response_model=list[CategoryWithProducts],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías con productos",
    description="Devuelve la lista de categorías del restaurante autenticado junto con sus productos."
)
def list_categories_with_products(
    user: User = Depends(waiter_or_admin),
    service: CategoryService = Depends(get_category_service)
):
    return service.list_categories_with_products(user.restaurant_id)

# ----------------------------------------------------------------------------------------------------
# Actualizar categoría
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar categoría",
    description="Actualiza una categoría del restaurante."
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    user: User = Depends(admin_only),
    service: CategoryService = Depends(get_category_service)
):
    return service.update_category(user.restaurant_id, category_id, data)

# ----------------------------------------------------------------------------------------------------
# Activar o desactivar categoría
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{category_id}/toggle",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Activar o desactivar categoría",
    description="Activa o desactiva una categoría del restaurante."
)
def toggle_category(
    category_id: int,
    user: User = Depends(admin_only),
    service: CategoryService = Depends(get_category_service)
):
    return service.toggle_category(user.restaurant_id, category_id)