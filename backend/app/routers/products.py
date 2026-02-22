from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.restaurant import Restaurant

from app.schemas.product import ProductCreate

from app.core.dependencies import get_current_restaurant

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/")
def create_product(
    product: ProductCreate,
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    db_product = Product(
        name=product.name,
        price=product.price,
        restaurant_id=restaurant.id,
        category_id=product.category_id,
        station_id=product.station_id
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

@router.get("/")
def list_products(
    restaurant: Restaurant = Depends(get_current_restaurant),
    db: Session = Depends(get_db)
):
    return db.query(Product).filter(
        Product.restaurant_id == restaurant.id,
        Product.active == True
    ).all()

