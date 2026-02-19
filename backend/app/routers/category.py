from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.category import Category
from app.models.product import Product

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/with-products")
def list_categories_with_products(db: Session = Depends(get_db)):

    categories = (
        db.query(Category)
        .options(joinedload(Category.products))
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
            if p.active
        ]

        result.append({
            "id": category.id,
            "name": category.name,
            "products": active_products
        })

    return result
