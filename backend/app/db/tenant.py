from sqlalchemy.orm import Session
from app.models.user import User

def tenant_query(db: Session, model, user: User):
    return db.query(model).filter(model.restaurant_id == user.restaurant_id)