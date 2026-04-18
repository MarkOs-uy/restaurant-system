from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.cash_register.cash_movement_service import CashMovementService


def get_cash_register_service():
    return CashRegisterService()

def get_cash_movement_service():
    return CashMovementService()