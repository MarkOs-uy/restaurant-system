from app.models.cash_movement import CashMovement
from app.models.cash_register import CashRegister
from app.domain.errors import CashRegisterDomainError
from app.models.user import UserRole
from app.services.event_service import event_service


class CashMovementService:

    def create_cash_movement(
        self,
        db,
        restaurant_id,
        user_id,
        movement_type,
        amount,
        reason
    ):

        cash_register = (
            db.query(CashRegister)
            .filter(
                CashRegister.restaurant_id == restaurant_id,
                CashRegister.closed_at == None
            )
            .first()
        )

        if not cash_register:
            raise CashRegisterDomainError("No hay caja abierta")

        movement = CashMovement(
            cash_register_id=cash_register.id,
            user_id=user_id,
            type=movement_type,
            amount=amount,
            reason=reason
        )

        db.add(movement)
        db.commit()
        db.refresh(movement)

        event_service.emit_to_role(
            restaurant_id,
            UserRole.CASHIER,
            {
                "type": "CASH_MOVEMENT_ADDED",
                "movement": {
                    "id": movement.id,
                    "type": movement.type,
                    "amount": float(movement.amount),
                    "reason": movement.reason,
                    "created_at": movement.created_at.isoformat()
                }
            }
        )

        return movement
    
    def delete_cash_movement(
        self,
        db,
        restaurant_id,
        movement_id
    ):

        movement = db.query(CashMovement).filter(
            CashMovement.id == movement_id
        ).first()

        if not movement:
            raise CashRegisterDomainError("Movimiento no encontrado")

        amount = movement.amount
        movement_type = movement.type

        db.delete(movement)
        db.commit()

        event_service.emit_to_role(
            restaurant_id,
            UserRole.CASHIER,
            {
                "type": "CASH_MOVEMENT_DELETED",
                "movement_id": movement_id,
                "amount": amount,
                "movement_type": movement_type
            }
        )

        return {"ok": True}