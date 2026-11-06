from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime, timezone


from app import models
from app.services.event_worker import EventWorker
from app.services.event_cleanup import EventCleanup
from app.db.session import engine
from app.events.redis_listener import redis_event_listener

from app.scheduler.scheduler import scheduler
from app.scheduler.backup_jobs import register_jobs

# routers
from app.routers import tables, orders, products, cash_register, category, order_items
from app.routers import layout, system_settings, stations, auth, users, kitchen, reports, backups

from app.domain.errors.base import DomainError
from app.websocket import ws
from app.core.config import CORS_ORIGINS
from app.core.redis import redis_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("app.main")

# --------------------------------------------------------------------------------------
# Configuración del ciclo de vida de la aplicación.
# --------------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Backend arrancando...")

    # Event worker
    worker = EventWorker()
    worker_task = asyncio.create_task(worker.run())
    logger.info("Event worker iniciado")

    # Redis listener
    redis_task = asyncio.create_task(redis_event_listener())
    logger.info("Redis listener iniciado")

    # Event cleanup
    cleanup = EventCleanup(interval_seconds=3600)
    cleanup_task = asyncio.create_task(cleanup.run())
    logger.info("Event cleanup iniciado")

    # Scheduler
    logger.info("Iniciando scheduler...")
    register_jobs()
    scheduler.start()
    logger.info("Scheduler iniciado")

    try:
        yield
    finally:
        logger.info("Backend apagándose...")

        # Detener scheduler
        scheduler.shutdown(wait=False)
        logger.info("Scheduler detenido")

        redis_task.cancel()
        worker_task.cancel()
        cleanup_task.cancel()

        await asyncio.gather(
            redis_task,
            worker_task,
            cleanup_task,
            return_exceptions=True,
        )
        logger.info("Redis listener detenido")
        logger.info("Event worker detenido")
        logger.info("Event cleanup detenido")

# --------------------------------------------------------------------------------------
# Aplicación FastAPI.
# --------------------------------------------------------------------------------------
app = FastAPI(lifespan=lifespan, redirect_slashes=False)

# --------------------------------------------------------------------------------------
# Configuración de archivos estáticos.
# --------------------------------------------------------------------------------------
uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# --------------------------------------------------------------------------------------
# Configuración CORS.
# --------------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------------------
# Registro de routers.
# --------------------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(backups.router, prefix="/api")
app.include_router(cash_register.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(kitchen.router, prefix="/api")
app.include_router(order_items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(tables.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(ws.router)
app.include_router(layout.router, prefix="/api")
app.include_router(system_settings.router, prefix="/api")

# --------------------------------------------------------------------------------------
# Endpoints del sistema.
# --------------------------------------------------------------------------------------
@app.get("/")
def root() -> dict[str, str]:
    return {"status": "running"}


BACKUP_DIR = Path(
    os.getenv("BACKUP_DIR", "/backups")
)


def get_latest_backup() -> dict:
    try:
        if not BACKUP_DIR.exists():
            return {
                "status": "missing",
                "last_backup_at": None,
            }

        backup_files = [
            path
            for path in BACKUP_DIR.iterdir()
            if path.is_file()
        ]

        if not backup_files:
            return {
                "status": "missing",
                "last_backup_at": None,
            }

        latest = max(
            backup_files,
            key=lambda path: path.stat().st_mtime,
        )

        modified_at = datetime.fromtimestamp(
            latest.stat().st_mtime,
            tz=timezone.utc,
        )

        return {
            "status": "ok",
            "last_backup_at": modified_at.isoformat(),
        }

    except Exception:
        return {
            "status": "error",
            "last_backup_at": None,
        }


@app.get("/health")
@app.get("/api/health")
async def health():
    database_ok = False
    redis_ok = False

    # -------------------------------------------------------------------------
    # PostgreSQL
    # -------------------------------------------------------------------------
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        database_ok = True

    except Exception:
        database_ok = False

    # -------------------------------------------------------------------------
    # Redis
    # -------------------------------------------------------------------------
    try:
        await redis_client.ping()
        redis_ok = True

    except Exception:
        redis_ok = False

    # -------------------------------------------------------------------------
    # Backups
    # -------------------------------------------------------------------------
    backup = get_latest_backup()

    # -------------------------------------------------------------------------
    # Estado general del servicio
    # -------------------------------------------------------------------------
    healthy = database_ok and redis_ok

    payload = {
        "status": "ok" if healthy else "error",
        "service": "restaurant-pos",
        "version": "1.0.0",
        "database": {
            "status": "ok" if database_ok else "error",
        },
        "redis": {
            "status": "ok" if redis_ok else "error",
        },
        "backup": backup,
    }

    return JSONResponse(
        status_code=200 if healthy else 503,
        content=payload,
    )

# --------------------------------------------------------------------------------------
# Manejadores globales de excepciones.
# --------------------------------------------------------------------------------------
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    logger.warning("%s: %s", exc.code, exc.message,)
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "detail": exc.message,
            "context": exc.context
        }
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unexpected server error")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "detail": "Error interno del servidor"
        }
    )
