from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user

from app.schemas.user import UserOut

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not pwd_context.verify(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value,
        "restaurant_id": user.restaurant_id
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserOut)
def get_me(
    user: User = Depends(get_current_user)
):
    return user