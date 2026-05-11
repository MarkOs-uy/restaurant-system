from fastapi import APIRouter, Depends

from app.models.user import User

from app.schemas.product import ProductCreate, ProductUpdate

from app.dependencies.roles import waiter_or_admin,admin_only

from app.domain.product.product_service import ProductService
from app.domain.product.dependencies import get_product_service


router = APIRouter(prefix="/products", tags=["products"])


@router.post("/")
def create_product(
    product: ProductCreate,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.create_product(
        user.restaurant_id,
        product
    )


@router.get("/")
def list_products(
    user: User = Depends(waiter_or_admin),
    service: ProductService = Depends(get_product_service)
):

    return service.list_products(user.restaurant_id)


@router.patch("/{product_id}")
def update_product(
    product_id: int,
    product: ProductUpdate,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.update_product(
        product_id,
        user.restaurant_id,
        product
    )


@router.patch("/{product_id}/toggle")
def toggle_product(
    product_id: int,
    user: User = Depends(admin_only),
    service: ProductService = Depends(get_product_service)
):
    return service.toggle_product(
        product_id,
        user.restaurant_id
    )