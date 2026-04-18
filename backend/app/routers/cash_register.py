from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.domain.errors import CashRegisterDomainError

from app.schemas.cash_register import (
    CashRegisterOpen,
    CashRegisterSummary,
    CashRegisterCloseOut,
    CashMovementCreate,
    CashRegisterClose,
    CashRegisterDashboard
)

from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.cash_register.cash_movement_service import CashMovementService
from app.domain.cash_register.dependencies import (
    get_cash_register_service,
    get_cash_movement_service
)

router = APIRouter(
    prefix="/cash-register",
    tags=["cash-register"]
)


@router.post("/open")
def open_cash_register(
    data: CashRegisterOpen,
    db: Session = Depends(get_db),
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(get_current_user)
):
    try:
        return service.open_cash_register(
            db=db,
            restaurant_id=user.restaurant_id,
            user_id=user.id,
            opening_amount=data.opening_amount
        )
    except CashRegisterDomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/close", response_model=CashRegisterCloseOut)
def close_cash_register(
    payload: CashRegisterClose,
    db: Session = Depends(get_db),
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(get_current_user)
):
    try:
        return service.close_cash_register(
            db=db,
            restaurant_id=user.restaurant_id,
            user_id=user.id,
            counted_cash=payload.counted_cash
        )
    except CashRegisterDomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/movements")
def create_cash_movement(
    payload: CashMovementCreate,
    db: Session = Depends(get_db),
    service: CashMovementService = Depends(get_cash_movement_service),
    user: User = Depends(get_current_user)
):
    try:
        return service.create_cash_movement(
            db=db,
            restaurant_id=user.restaurant_id,
            user_id=user.id,
            movement_type=payload.type,
            amount=payload.amount,
            reason=payload.reason
        )
    except CashRegisterDomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/movements/{movement_id}")
def delete_cash_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    service: CashMovementService = Depends(get_cash_movement_service),
    user: User = Depends(get_current_user)
):
    try:
        return service.delete_cash_movement(
            db=db,
            restaurant_id=user.restaurant_id,
            movement_id=movement_id
        )
    except CashRegisterDomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/current", response_model=CashRegisterSummary | None)
def current_cash_register(
    db: Session = Depends(get_db),
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(get_current_user)
):
    return service.get_current_cash_register(
        db=db,
        restaurant_id=user.restaurant_id
    )


@router.get("/dashboard", response_model=CashRegisterDashboard | None)
def get_cash_register_dashboard(
    db: Session = Depends(get_db),
    service: CashRegisterService = Depends(get_cash_register_service),
    user: User = Depends(get_current_user)
):
    return service.get_dashboard(
        db=db,
        restaurant_id=user.restaurant_id
    )