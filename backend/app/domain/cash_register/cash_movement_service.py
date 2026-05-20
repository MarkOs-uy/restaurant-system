from sqlalchemy.orm import Session
from app.models.cash_movement import CashMovement
from app.models.cash_register import CashRegister
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.models.user import UserRole
from app.services.event_service import EventService
from app.utils.money import money


class CashMovementService:

    def __init__(self, db: Session):
        self.db = db
        self.events = EventService(db)


    # -------------------------
    # Crear movimiento de caja
    # -------------------------

    def create_cash_movement(
        self,
        restaurant_id,
        user_id,
        movement_type,
        amount,
        reason
    ):
        cash_register = (
            self.db.query(CashRegister)
            .filter(
                CashRegister.restaurant_id == restaurant_id,
                CashRegister.is_open == True
            )
            .with_for_update()
            .first()
        )
        if not cash_register:
            raise DomainError(
                "cash register not open",
                ErrorCode.CASH_REGISTER_NOT_OPEN
            )
        movement = CashMovement(
            cash_register_id=cash_register.id,
            user_id=user_id,
            type=movement_type,
            amount=amount,
            reason=reason
        )
        self.db.add(movement)
        self.db.flush()
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type="CASH_MOVEMENT_ADDED",
            payload={
                "movement": {
                    "id": movement.id,
                    "type": movement.type,
                    "amount": money(movement.amount),
                    "reason": movement.reason,
                    "created_at": movement.created_at.isoformat()
                }
            },
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.commit()
        self.db.refresh(movement)

        return movement

    # -------------------------
    # Eliminar movimiento de caja
    # -------------------------

    def delete_cash_movement(
        self,
        restaurant_id,
        movement_id
    ):
        movement = self.db.query(CashMovement).join(
            CashRegister,
            CashMovement.cash_register_id == CashRegister.id
        ).filter(
            CashMovement.id == movement_id,
            CashRegister.restaurant_id == restaurant_id
        ).first()

        if not movement:
            raise DomainError(
                "Movement not found",
                ErrorCode.CASH_MOVEMENT_NOT_FOUND
            )

        amount = movement.amount
        movement_type = movement.type

        self.db.delete(movement)
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type="CASH_MOVEMENT_DELETED",
            payload={
                "movement_id": movement_id,
                "amount": money(amount),
                "movement_type": movement_type
            },
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.commit()
        return {"ok": True}