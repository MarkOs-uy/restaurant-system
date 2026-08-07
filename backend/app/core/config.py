import os

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------------------
# Obtiene una variable de entorno separada por comas como lista de strings.
# --------------------------------------------------------------------------------------
def _get_csv_env(
    name: str,
    default: str
) -> list[str]:
    value = os.getenv(name, default)
    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]

# --------------------------------------------------------------------------------------
# Obtiene una variable de entorno como entero.
# --------------------------------------------------------------------------------------
def _get_int_env(
    name: str,
    default: int
) -> int:
    return int(
        os.getenv(name, str(default))
    )

# --------------------------------------------------------------------------------------
# Obtiene una variable de entorno obligatoria.
# Lanza RuntimeError si no está definida.
# --------------------------------------------------------------------------------------
def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"{name} no está configurada. Defínela en el archivo .env"
        )
    return value


SECRET_KEY = _get_required_env("SECRET_KEY")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = _get_int_env("ACCESS_TOKEN_EXPIRE_MINUTES",60)

CORS_ORIGINS = _get_csv_env("CORS_ORIGINS","")

if not CORS_ORIGINS:
    raise RuntimeError(
        "CORS_ORIGINS debe configurarse explícitamente"
    )
