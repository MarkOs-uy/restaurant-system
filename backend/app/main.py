from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine

from contextlib import asynccontextmanager
from app.db.session import SessionLocal
from app.seed import seed_tables

# IMPORTANTE: importar modelos
from app import models

from app.routers import tables, orders, products, cash_register

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Iniciando aplicación...")

    db = SessionLocal()

    try:
        #seed_tables(db)
        print("Iniciando aplicación...")
    finally:
        db.close()

    yield

    print("Apagando aplicación...")

app = FastAPI(lifespan=lifespan)


app.include_router(tables.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(cash_register.router)

#Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "running"}
