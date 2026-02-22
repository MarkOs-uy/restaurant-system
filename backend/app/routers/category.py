from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.category import Category
from app.models.product import Product
from app.core.dependencies import get_current_restaurant

from app.models.restaurant import Restaurant

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/with-products")
def list_categories_with_products(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    categories = (
        db.query(Category)
        .options(joinedload(Category.products))
        .filter(Category.restaurant_id == restaurant.id)
        .order_by(Category.name)
        .all()
    )

    result = []

    for category in categories:
        active_products = [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price
            }
            for p in category.products
            if p.active and p.restaurant_id == restaurant.id
        ]

        result.append({
            "id": category.id,
            "name": category.name,
            "products": active_products
        })

    return result
