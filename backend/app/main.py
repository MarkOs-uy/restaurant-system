from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine

from contextlib import asynccontextmanager
from app.db.session import SessionLocal
from app.seed import seed_tables

from app import models

from app.routers import tables, orders, products, cash_register, category, order_items, stations, auth, users, ws_kitchen
from app.routers.kitchen import router as kitchen_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Backend arrancando...")
    yield
    print("Backend apagándose...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # luego lo restringimos
    #allow_origins=["http://localhost:5173","http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(cash_register.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(kitchen_router, prefix="/api")
app.include_router(order_items.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(tables.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(ws_kitchen.router)
@app.get("/")
def root():
    return {"status": "running"}
