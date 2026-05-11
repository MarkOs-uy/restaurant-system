import os

from dotenv import load_dotenv


load_dotenv()


def _get_csv_env(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no está configurada. Defínela en el archivo .env")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

CORS_ORIGINS = _get_csv_env("CORS_ORIGINS", "")
if not CORS_ORIGINS:
    raise RuntimeError("CORS_ORIGINS debe configurarse explícitamente")
