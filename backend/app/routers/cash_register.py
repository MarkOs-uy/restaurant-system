from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from sqlalchemy import func
from app.models.payment import Payment

from app.db.session import get_db
from app.models.cash_register import CashRegister
from app.schemas.cash_register import CashRegisterOpen

router = APIRouter(
    prefix="/cash-register",
    tags=["Cash Register"]
)

@router.post("/open")
def open_cash_register(
    restaurant_id: int,
    opening_amount: float,
    db: Session = Depends(get_db)
):
    existing = db.query(CashRegister).filter(
        CashRegister.closed_at == None,
        CashRegister.restaurant_id == restaurant_id
    ).first()

    if existing:
        raise HTTPException(400, "Ya hay una caja abierta")

    register = CashRegister(
        restaurant_id=restaurant_id,
        opening_amount=opening_amount
    )

    db.add(register)
    db.commit()
    db.refresh(register)

    return register


@router.post("/close")
def close_cash_register(db: Session = Depends(get_db)):

    cash_register = db.query(CashRegister).filter(
        CashRegister.closed_at == None
    ).first()

    if not cash_register:
        raise HTTPException(400, "No hay caja abierta")

    total = db.query(
        func.coalesce(func.sum(Payment.total), 0)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    cash_register.closing_amount = total
    cash_register.closed_at = func.now()

    db.commit()
    db.refresh(cash_register)

    return {
        "message": "Caja cerrada",
        "total_vendido": total
    }

@router.get("/current")
def current_cash_register(db: Session = Depends(get_db)):

    cash_register = db.query(CashRegister).filter(
        CashRegister.closed_at == None
    ).first()
    
    if not cash_register:
        raise HTTPException(400, "No hay caja abierta")

    total_sales = db.query(
        func.coalesce(func.sum(Payment.total), 0)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    orders_count = db.query(func.count(Payment.id)).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    average_ticket = 0
    if orders_count > 0:
        average_ticket = total_sales / orders_count

    rows = db.query(
        Payment.method,
        func.sum(Payment.total)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).group_by(
        Payment.method
    ).all()

    by_method = {method: float(amount) for method, amount in rows}

    return {
        "cash_register_id": cash_register.id,
        "opened_at": cash_register.opened_at,
        "total_sales": total_sales,
        "orders_count": orders_count,
        "average_ticket": average_ticket,
        "by_method": by_method
    }


