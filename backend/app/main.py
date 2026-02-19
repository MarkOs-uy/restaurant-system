from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine

from contextlib import asynccontextmanager
from app.db.session import SessionLocal
from app.seed import seed_tables

from app import models

from app.routers import tables, orders, products, cash_register, category, order_items, stations

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

app.include_router(tables.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(cash_register.router)
app.include_router(category.router)

@app.get("/")
def root():
    return {"status": "running"}
