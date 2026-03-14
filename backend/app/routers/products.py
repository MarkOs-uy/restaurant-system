from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.product import Product
from app.models.restaurant import Restaurant
from app.models.user import User

from app.schemas.product import ProductCreate

from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/")
def create_product(
    product: ProductCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_product = Product(
        name=product.name,
        price=product.price,
        restaurant_id=user.restaurant_id,
        category_id=product.category_id,
        station_id=product.station_id
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

@router.get("/")
def list_products(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.station)
    ).filter(
        Product.restaurant_id == user.restaurant_id
    ).all()

@router.patch("/{product_id}")
def update_product(
    product_id: int,
    product: ProductCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.restaurant_id == user.restaurant_id
    ).first()

    if not db_product:
        raise HTTPException(404, "Product not found")

    db_product.name = product.name
    db_product.price = product.price
    db_product.category_id = product.category_id
    db_product.station_id = product.station_id

    db.commit()
    db.refresh(db_product)

    return db_product

@router.patch("/{product_id}/toggle")
def toggle_product(
    product_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.restaurant_id == user.restaurant_id
    ).first()

    if not product:
        raise HTTPException(404, "Product not found")

    product.active = not product.active

    db.commit()
    db.refresh(product)

    return product