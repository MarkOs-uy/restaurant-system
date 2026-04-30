from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.cash_register.cash_movement_service import CashMovementService

def get_cash_register_service(
    db: Session = Depends(get_db)
) -> CashRegisterService:
    return CashRegisterService(db)


def get_cash_movement_service(
    db: Session = Depends(get_db)
) -> CashMovementService:
    return CashMovementService(db)