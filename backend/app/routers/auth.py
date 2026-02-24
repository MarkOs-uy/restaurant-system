from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.models.user import User
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.name == form_data.username
    ).first()

    if not user:
        raise HTTPException(400, "Invalid credentials")

    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(400, "Invalid credentials")

    token = create_access_token({
        "sub": str(user.id)
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role.value
    }

