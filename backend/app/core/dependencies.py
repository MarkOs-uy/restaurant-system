from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.restaurant import Restaurant


def get_current_restaurant(
    x_restaurant_id: int = Header(None),
    db: Session = Depends(get_db)
):
    """
    Temporal: identifica restaurante por header.
    En producción esto vendrá del JWT.
    """

    if not x_restaurant_id:
        raise HTTPException(
            status_code=400,
            detail="X-Restaurant-Id header required"
        )

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == x_restaurant_id,
        Restaurant.active == True
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    return restaurant
