"""
Endpoints para la gestión de la autenticación de usuarios.
Todas las operaciones trabajan únicamente sobre el restaurante autenticado.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.dependencies.auth import get_current_user
from app.core.security import create_access_token, verify_password

from app.models.user import User

from app.schemas.auth import TokenResponse
from app.schemas.user import UserOut

logger = logging.getLogger("app.routers.auth")

router = APIRouter(prefix="/auth", tags=["auth"])

# ----------------------------------------------------------------------------------------------------
# Autenticar usuario
# ----------------------------------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica un usuario y devuelve un JWT."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning("Login fallido username=%s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    logger.info("Login exitoso user=%s r=%s", user.id, user.restaurant_id)
    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value,
        "restaurant_id": user.restaurant_id
    })
    return TokenResponse(access_token=token, token_type="bearer")

# ----------------------------------------------------------------------------------------------------
# Obtener datos del usuario autenticado
# ----------------------------------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Usuario autenticado",
    description="Devuelve la información del usuario autenticado."
)
def get_me(user: User = Depends(get_current_user)):
    return user