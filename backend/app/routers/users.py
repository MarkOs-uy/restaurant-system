from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from passlib.context import CryptContext

from app.db.session import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user

from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", response_model=list[UserOut])
def list_users(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(User).filter(
        User.restaurant_id == user.restaurant_id
    ).all()


@router.post("/")
def create_user(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    hashed = pwd_context.hash(data["password"])

    new_user = User(
        username=data["username"],
        password_hash=hashed,
        role=data["role"],
        restaurant_id=user.restaurant_id,
        active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    target = db.query(User).filter(
        User.id == user_id,
        User.restaurant_id == user.restaurant_id
    ).first()

    if not target:
        raise HTTPException(404, "User not found")

    target.username = data["username"]
    target.role = data["role"]

    if data.get("password"):
        target.password_hash = pwd_context.hash(data["password"])

    db.commit()
    db.refresh(target)

    return target


@router.patch("/{user_id}/toggle")
def toggle_user(
    user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    target = db.query(User).filter(
        User.id == user_id,
        User.restaurant_id == user.restaurant_id
    ).first()

    if not target:
        raise HTTPException(404, "User not found")

    target.active = not target.active

    db.commit()
    db.refresh(target)

    return target