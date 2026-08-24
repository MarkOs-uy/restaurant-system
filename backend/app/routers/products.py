"""
Endpoints para la gestión de productos.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""

from fastapi import(
    APIRouter, 
    Depends, 
    status,
    Query
)

from app.dependencies.roles import (
    admin_only, 
    waiter_or_admin
)

from app.domain.product.dependencies import get_product_service
from app.domain.product.product_service import ProductService

from app.models.user import User

from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter(prefix="/products", tags=["products"])

# ----------------------------------------------------------------------------------------------------
# Crear producto
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Crea un nuevo producto para el restaurante autenticado."
)
def create_product(
    product: ProductCreate,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.create_product(user.restaurant_id, product)

# ----------------------------------------------------------------------------------------------------
# Listar productos
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos",
    description="Devuelve la lista de productos del restaurante autenticado."
)
def list_products(
    active: bool | None = Query(default=True),
    user: User = Depends(waiter_or_admin),
    service: ProductService = Depends(get_product_service)
):
    return service.list_products(
        user.restaurant_id,
        active
    )

# ----------------------------------------------------------------------------------------------------
# Actualizar producto
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto",
    description="Actualiza un producto del restaurante autenticado."
)
def update_product(
    product_id: int,
    product: ProductUpdate,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.update_product(product_id, user.restaurant_id, product)

# ----------------------------------------------------------------------------------------------------
# Alternar estado del producto (Activo/Inactivo)
# ----------------------------------------------------------------------------------------------------
@router.patch(
    "/{product_id}/toggle",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Alternar estado del producto",
    description="Alterna el estado de un producto (Activo/Inactivo) del restaurante autenticado."
)
def toggle_product(
    product_id: int,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.toggle_product(product_id, user.restaurant_id)