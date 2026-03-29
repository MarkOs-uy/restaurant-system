from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app import models
from app.events.redis_listener import redis_event_listener

# routers
from app.routers import tables, orders, products, cash_register, category, order_items, stations, auth, users, kitchen
from app.websocket import ws

from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Backend arrancando...")

    # Redis listener
    redis_task = asyncio.create_task(redis_event_listener())

    yield

    print("Backend apagándose...")

    redis_task.cancel()


app = FastAPI(lifespan=lifespan)

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