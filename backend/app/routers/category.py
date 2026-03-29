from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.category import CategoryResponse, CategoryCreate, CategoryWithProducts
from app.domain.category.category_service import CategoryService
from app.domain.category.dependencies import get_category_service


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return service.list_categories(user.restaurant_id)


@router.post("/", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return service.create_category(user.restaurant_id, data.name)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryCreate,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return service.update_category(user.restaurant_id, category_id, data.name)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    service.delete_category(user.restaurant_id, category_id)
    return {"ok": True}


@router.get("/with-products", response_model=list[CategoryWithProducts])
def list_categories_with_products(
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service)
):
    return service.list_categories_with_products(user.restaurant_id)