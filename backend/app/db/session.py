from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATABASE_URL

# --------------------------------------------------------------------------------------
# Motor principal de SQLAlchemy
# --------------------------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# --------------------------------------------------------------------------------------
# Fábrica de sesiones de base de datos
# --------------------------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# --------------------------------------------------------------------------------------
# Dependency de FastAPI que proporciona una sesión de base de datos.
# La sesión se cierra automáticamente al finalizar la petición.
# --------------------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()