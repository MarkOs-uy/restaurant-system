from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    db_product = Product(
        name=product.name,
        price=product.price
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

@router.get("/")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.active == True).all()
