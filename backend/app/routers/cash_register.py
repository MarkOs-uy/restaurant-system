from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from sqlalchemy import func
from app.models.payment import Payment
from app.models.cash_register import CashRegister
from app.models.restaurant import Restaurant
from app.models.user import User

from app.db.session import get_db

from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/cash-register",
    tags=["Cash Register"]
)

@router.post("/open")
def open_cash_register(
    opening_amount: float,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(CashRegister).filter(
        CashRegister.closed_at == None,
        CashRegister.restaurant_id == user.restaurant_id
    ).first()

    if existing:
        raise HTTPException(400, "Ya hay una caja abierta")

    register = CashRegister(
        restaurant_id=user.restaurant_id,
        opening_amount=opening_amount
    )

    db.add(register)
    db.commit()
    db.refresh(register)

    return register


@router.post("/close")
def close_cash_register(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cash_register = db.query(CashRegister).filter(
        CashRegister.closed_at == None,
        CashRegister.restaurant_id == user.restaurant_id
    ).first()

    if not cash_register:
        raise HTTPException(400, "No hay caja abierta")

    total = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    cash_register.closing_amount = total
    cash_register.closed_at = func.now()

    db.commit()
    db.refresh(cash_register)

    return {
        "message": "Caja cerrada",
        "total_vendido": float(total)
    }


@router.get("/current")
def current_cash_register(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cash_register = db.query(CashRegister).filter(
        CashRegister.closed_at == None,
        CashRegister.restaurant_id == user.restaurant_id
    ).first()

    if not cash_register:
        raise HTTPException(400, "No hay caja abierta")

    total_sales = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    orders_count = db.query(func.count(Payment.id)).filter(
        Payment.cash_register_id == cash_register.id
    ).scalar()

    average_ticket = float(total_sales / orders_count) if orders_count else 0

    rows = db.query(
        Payment.method,
        func.sum(Payment.amount)
    ).filter(
        Payment.cash_register_id == cash_register.id
    ).group_by(
        Payment.method
    ).all()

    by_method = {method.value: float(amount) for method, amount in rows}

    return {
        "cash_register_id": cash_register.id,
        "opened_at": cash_register.opened_at,
        "total_sales": float(total_sales),
        "orders_count": orders_count,
        "average_ticket": average_ticket,
        "by_method": by_method
    }
