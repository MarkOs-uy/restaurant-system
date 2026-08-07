"""
Funciones de seguridad del sistema.

Responsabilidades:
- Generar hashes BCrypt.
- Verificar contraseñas.
- Crear tokens JWT.
- Validar y decodificar tokens JWT.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)

# --------------------------------------------------------------------------------------
# Contexto utilizado para el hash y verificación de contraseñas
# --------------------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --------------------------------------------------------------------------------------
# Genera el hash BCrypt de una contraseña
# --------------------------------------------------------------------------------------
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --------------------------------------------------------------------------------------
# Verifica una contraseña contra su hash BCrypt
# --------------------------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --------------------------------------------------------------------------------------
# Crea un JWT firmado con la información suministrada
# --------------------------------------------------------------------------------------
def create_access_token(data: dict[str, object]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **data,
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        "jti": str(uuid4()) # Identificador único del token
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# --------------------------------------------------------------------------------------
# Decodifica un JWT y devuelve su payload si es válido
# --------------------------------------------------------------------------------------
def decode_access_token(token: str) -> dict[str, object] | None:
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        return None