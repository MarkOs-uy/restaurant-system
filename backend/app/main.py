from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging

from app import models
from app.events.redis_listener import redis_event_listener

from app.services.event_service import event_service

# routers
from app.routers import tables, orders, products, cash_register, category, order_items, stations, auth, users, kitchen
from app.routers import layout


from app.domain.errors.base import DomainError
from app.websocket import ws

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Backend arrancando...")

    # 🔥 REGISTRAR EVENT LOOP PARA EVENT SERVICE
    event_service.loop = asyncio.get_running_loop()

    print("EventService loop registrado")

    # Redis listener
    redis_task = asyncio.create_task(redis_event_listener())

    yield

    print("Backend apagándose...")

    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan, redirect_slashes=False)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(auth.router, prefix="/api")
app.include_router(cash_register.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(kitchen.router, prefix="/api")
app.include_router(order_items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(tables.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(ws.router)
app.include_router(layout.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "restaurant-pos",
        "version": "1.0.0"
    }

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("app")

@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):

    logger.warning(f"{exc.code}: {exc.message}")

    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "detail": exc.message,
            "context": exc.context
        }
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):

    logger.exception("Unexpected server error")

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "detail": "Error interno del servidor"
        }
    )